import sys
from typing import Annotated

from bson import ObjectId
from decouple import config
from fastapi import APIRouter, Depends, HTTPException
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


@router.post("/all", dependencies=[Depends(JWTBearer())])
async def get_all_apps(token: Annotated[str, Depends(JWTBearer())]):
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
