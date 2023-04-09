import json
import sys

from decouple import config
from fastapi import APIRouter, Body
from pymongo import MongoClient

from utils.jwt_handler import signJWT
from utils.model import UserLoginSchema, UserSchema
from utils.validate import check_user

router = APIRouter()

sys.path.append("..")

mongokey = config("mongoKey")
client = MongoClient(mongokey)


def user_helper_read(user) -> dict:
    return {
        "id": str(user["id"]),
        "name": user["developerName"],
        "role": user["Role"],
        "email": user["email"],
        "password": user["password"],
        "appids": user["Appids"],
    }


def user_helper_register(user) -> dict:
    return {
        "name": user.name,
        "role": user.role,
        "email": user.email,
        "password": user.password,
    }


@router.get("/")
# This will get current user! TODO CHANGE
async def read_users():
    db = client["userDB"]
    collection = db.userCollection
    users = []
    for x in collection.find({}):
        users.append(user_helper_read(x))

    return json.dumps(users)


@router.get("/all")
async def all_users():
    db = client["userDB"]
    collection = db.userCollection
    users = []
    for x in collection.find({}):
        users.append(user_helper_read(x))

    return json.dumps(users)


@router.post("/signup")
def create_user(user=Body(...)):
    db = client["userDB"]
    collection = db.userCollection
    collection.insert_one(user)
    return signJWT(user["email"])


@router.post("/login")
def user_login(user=Body(...)):
    db = client["userDB"]
    collection = db.userCollection

    users = collection.find_one({"email": user["email"]})

    if users is None:
        return {"error": "Wrong login details!"}

    if check_user(user, users):
        return signJWT(user["email"])

    return {"error": "Wrong login details!"}
