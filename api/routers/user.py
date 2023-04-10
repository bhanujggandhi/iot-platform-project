import json
import sys

from decouple import config
from fastapi import APIRouter, Body
from passlib.context import CryptContext
from pymongo import MongoClient

from utils.jwt_handler import signJWT
from utils.model import UserLoginSchema, UserSchema
from utils.validate import check_user

router = APIRouter()

sys.path.append("..")

mongokey = config("mongoKey")
client = MongoClient(mongokey)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ===================================
# Password utilites
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# ===================================


def user_helper_read(user) -> dict:
    return {
        "id": str(user["id"]),
        "name": user["developerName"],
        "role": user["Role"],
        "email": user["email"],
        "password": user["password"],
        "appids": user["Appids"],
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
    user["password"] = get_password_hash(user["password"])
    collection.insert_one(user)
    return signJWT(user["email"])


@router.post("/login")
def user_login(user=Body(...)):
    db = client["userDB"]
    collection = db.userCollection

    found_user = collection.find_one({"email": user["email"]})

    if found_user is None:
        return {"error": "Wrong login details!"}

    if verify_password(user["password"], found_user["password"]):
        return signJWT(user["email"])

    return {"error": "Wrong login details!"}
