import json
import sys
from typing import Annotated

import requests
from bson import ObjectId
from decouple import config
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from utils.jwt_bearer import JWTBearer
from utils.jwt_handler import decodeJWT, signJWT
from utils.Messenger import Produce
from utils.Schema.app import AppRegister

sys.path.append("..")

router = APIRouter()
produce = Produce()


CONTAINER_NAME = config("deploy_app_container_name")
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]
app_collection = db.App
user_collection = db.User

loggerdb = client["LoggerDB"]
log_collection = loggerdb.loggingCollection
# ===================================
# Database decoding utility


def user_helper_read(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "role": user["role"],
        "email": user["email"],
    }


def populate_user(app):
    user_id = app["user"]
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    app["user"] = user_helper_read(user)
    return app


def apps_helper_read(app) -> dict:
    app = populate_user(app)
    return {
        "id": str(app["_id"]),
        "name": app["name"],
        "user": str(app["user"]),
        "ip": app["ip"],
        "port": app["port"],
        "active": app["active"],
    }


# ===================================


@router.post("/all")
async def get_all_apps():
    apps = []
    for x in app_collection.find({}):
        apps.append(apps_helper_read(x))

    return {"status": 200, "data": apps}


@router.post("/me", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())]):
    curr_user = decodeJWT(token)
    apps = []
    for x in app_collection.find({"user": ObjectId(curr_user["id"])}):
        apps.append(apps_helper_read(x))

    return {"status": 200, "data": apps}


@router.post("/register", dependencies=[Depends(JWTBearer())])
async def register_new_app(
    token: Annotated[str, Depends(JWTBearer())], app: AppRegister = Body(...)
):
    try:
        curr_user = decodeJWT(token)

        user_collection.find_one({"_id": ObjectId(curr_user["id"])})

        app_collection.create_index("name", unique=True)

        result = app_collection.insert_one(
            {
                "name": app.name,
                "user": ObjectId(curr_user["id"]),
                "sensor_types": app.sensor_types,
                "binded_sensors": app.binded_sensors,
                "active": False,
                "ip": "",
                "port": -1,
            }
        )

        payload = {
            "id": str(result.inserted_id),
            "user": curr_user["id"],
            "token": "app",
        }

        return {
            "status_code": 200,
            "token": signJWT(payload),
        }
    except DuplicateKeyError:
        return {"message": "App with this name already exists.", "status_code": 400}


@router.post("/{appid}/stop", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())], appid: str):
    curr_user = decodeJWT(token)
    curr_app = app_collection.find_one(
        {"name": appid, "user": ObjectId(curr_user["id"])}
    )
    if not curr_app:
        return {
            "status": 404,
            "data": f"We have no app deployed in the name of {appid}",
        }

    if str(curr_app["user"]) != curr_user["id"]:
        return {"status": 401, "data": f"You are not authorized to do that"}
    message = {
        "service": "",
        "app": appid,
        "operation": "stop",
        "appid": str(curr_app["_id"]),
        "userid": curr_user["id"],
        "src": "topic_internal_api",
    }
    produce.push("topic_node_manager", "", json.dumps(message))

    return {"status": 200, "data": "We have stopped your app successfully"}


@router.post("/{appid}/start", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())], appname: str):
    curr_user = decodeJWT(token)
    curr_app = app_collection.find_one(
        {"name": appname, "user": ObjectId(curr_user["id"])}
    )
    if not curr_app:
        return {
            "status": 404,
            "data": f"We have no app deployed in the name of {appname}",
        }

    if str(curr_app["user"]) != curr_user["id"]:
        return {"status": 401, "data": f"You are not authorized to do that"}

    message = {
        "service": "",
        "app": appname,
        "operation": "start",
        "appid": str(curr_app["_id"]),
        "userid": curr_user["id"],
        "src": "topic_internal_api",
    }

    produce.push("topic_node_manager", "", json.dumps(message))

    return {"status": 200, "data": "We have started your app successfully"}


@router.post("/{appid}/remove", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())], appname: str):
    curr_user = decodeJWT(token)
    curr_app = app_collection.find_one(
        {"name": appname, "user": ObjectId(curr_user["id"])}
    )
    if not curr_app:
        return {
            "status": 404,
            "data": f"We have no app deployed in the name of {appname}",
        }

    if str(curr_app["user"]) != curr_user["id"]:
        return {"status": 401, "data": f"You are not authorized to do that"}

    message = {
        "service": "",
        "app": appname,
        "operation": "remove",
        "appid": str(curr_app["_id"]),
        "userid": curr_user["id"],
        "src": "topic_internal_api",
    }

    produce.push("topic_node_manager", "", json.dumps(message))

    return {"status": 200, "data": "We have removed your app successfully"}


@router.post("/{appid}/logs", dependencies=[Depends(JWTBearer())])
async def get_logs(token: Annotated[str, Depends(JWTBearer())], app_name: str = None):
    curr_user = decodeJWT(token)
    curr_app = app_collection.find_one(
        {"name": appname, "user": ObjectId(curr_user["id"])}
    )
    if not curr_app:
        return {
            "status": 404,
            "data": f"We have no app deployed in the name of {appname}",
        }

    if str(curr_app["user"]) != curr_user["id"]:
        return {"status": 401, "data": f"You are not authorized to do that"}

    # find all data in DB for given app name
    cursor = log_collection.find({"app_name": app_name}, sort=[("timestamp", 1)])

    output = ""
    # Sort the documents on the basis of their created time and display onto stdout
    for document in cursor:
        output += f'<br>{document["timestamp"]} | {document["level"]} <b>({document["app_name"]}, {document["user_id"]})</b>: {document["msg"]}'

    HTML_output = (
        """        
    <html>
    <head>
        LOGS
    </head>
    <body>
    """
        + output
        + """
    </body>
    </html>
    """
    )

    return HTMLResponse(content=HTML_output, status_code=200)


@router.get("/app/{app_name:path}")
async def apps(app_name: str = Path(...)):
    print(app_name)
    arr = app_name.split("/")
    ret = app_collection.find_one({"name": arr[0]})
    if ret == None:
        return HTMLResponse(
            content="""<html><head><title>some title</title></head><body><h1>Invalid Application</h1></body></html>""",
            status_code=400,
        )
    else:
        if ret["active"] == False:
            return HTMLResponse(
                content="""<html><head><title>some title</title></head><body><h1>Application is not Running</h1></body></html>""",
                status_code=400,
            )
        else:
            url = "http://" + ret["ip"] + ":" + str(ret["port"])
            for i in range(1, len(arr)):
                url += "/" + str(arr[i])
            print(url)
            response = requests.get(url).json()

    return HTMLResponse(content=response, status_code=200)
