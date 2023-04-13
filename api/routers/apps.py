import json
import sys
from typing import Annotated

import requests
from bson import ObjectId
from decouple import config
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from utils.jwt_bearer import JWTBearer
from utils.jwt_handler import decodeJWT
from utils.Messenger import Produce

sys.path.append("..")

router = APIRouter()
produce = Produce()


CONTAINER_NAME = config("deploy_app_container_name")
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]
app_collection = db.App
user_collection = db.User


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
    return {"id": str(app["_id"]), "name": app["name"], "user": str(app["user"]), "ip": app["ip"], "port": app["port"]}


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


@router.post("/{appid}/stop", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())], appid: str):
    curr_user = decodeJWT(token)
    curr_app = app_collection.find_one({"name": appid})
    if not curr_app:
        return {"status": 404, "data": f"We have no app deployed in the name of {appid}"}

    if str(curr_app["_id"]) != curr_user["id"]:
        return {"status": 401, "data": f"You are not authorized to do that"}

    message = {"service": "", "app": appid, "operation": "stop", "id": curr_user["id"], "src": "topic_internal_api"}
    produce.push("topic_node_manager", "", json.dumps(message))

    return {"status": 200, "data": "We have stopped your app successfully"}


@router.post("/{appid}/start", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())], appid: str):
    curr_user = decodeJWT(token)
    curr_app = app_collection.find_one({"name": appid})
    if not curr_app:
        return {"status": 404, "data": f"We have no app deployed in the name of {appid}"}

    if str(curr_app["_id"]) != curr_user["id"]:
        return {"status": 401, "data": f"You are not authorized to do that"}

    message = {"service": "", "app": appid, "operation": "start", "id": curr_user["id"], "src": "topic_internal_api"}
    produce.push("topic_node_manager", "", json.dumps(message))

    return {"status": 200, "data": "We have started your app successfully"}


@router.post("/{appid}/remove", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())], appid: str):
    curr_user = decodeJWT(token)
    curr_app = app_collection.find_one({"name": appid})
    if not curr_app:
        return {"status": 404, "data": f"We have no app deployed in the name of {appid}"}

    if str(curr_app["_id"]) != curr_user["id"]:
        return {"status": 401, "data": f"You are not authorized to do that"}

    message = {"service": "", "app": appid, "operation": "remove", "id": curr_user["id"], "src": "topic_internal_api"}
    produce.push("topic_node_manager", "", json.dumps(message))

    return {"status": 200, "data": "We have removed your app successfully"}


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