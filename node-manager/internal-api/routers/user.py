import json
import sys
from enum import Enum
from typing import Annotated, List

from bson import ObjectId
from decouple import config
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, status
from passlib.context import CryptContext
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from utils.jwt_bearer import JWTBearer
from utils.jwt_handler import decodeJWT, signJWT
from utils.Schema.user import User, UserLogin

router = APIRouter()

sys.path.append("..")

mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ===================================
# Password utilites
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password.encode("utf-8"))


# ===================================


# ===================================
# Database decoding utility
def user_helper_read(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "role": user["role"],
        "email": user["email"],
    }


# ===================================


@router.post("/signup")
def create_user(user: User = Body(...)):
    collection = db.User
    collection.create_index("email", unique=True)
    try:
        user.password = get_password_hash(user.password)
        result = collection.insert_one(user.dict())
        payload = {
            "id": str(result.inserted_id),
            "name": user.name,
            "role": user.role,
            "email": user.email,
            "token": "user",
        }
        return {"status_code": 200, "token": signJWT(payload)}
    except DuplicateKeyError:
        return {"message": "User with this email already exists.", "status_code": 400}


@router.post("/login")
def user_login(user: UserLogin = Body(...)):
    collection = db.User

    found_user = collection.find_one({"email": user.email})

    if found_user:
        password = verify_password(
            user.password.encode("utf-8"), found_user["password"]
        )
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        payload = {
            "id": str(found_user["_id"]),
            "name": found_user["name"],
            "role": found_user["role"],
            "email": found_user["email"],
            "token": "user",
        }
        return signJWT(payload)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )


@router.get("/", dependencies=[Depends(JWTBearer())])
async def all_users():
    collection = db.User
    users = []
    for x in collection.find({}):
        users.append(user_helper_read(x))

    return {"status": "200", "data": users}


@router.get("/me", dependencies=[Depends(JWTBearer())])
async def get_curr_user(token: Annotated[str, Depends(JWTBearer())]):
    curr_user = decodeJWT(token)
    collection = db.User
    user = collection.find_one({"_id": ObjectId(curr_user["id"])})
    return {"status": "200", "data": user_helper_read(user)}
