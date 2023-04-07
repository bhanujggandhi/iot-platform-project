import sys

from fastapi import APIRouter, Body
from utils.model import UserLoginSchema, UserSchema
from utils.jwt_handler import signJWT
from utils.validate import check_user

router = APIRouter()

sys.path.append("..")

users = []


@router.get("/", tags=["user"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/all", tags=["user"])
async def all_users():
    return users


@router.post("/signup", tags=["user"])
def create_user(user: UserSchema = Body(...)):
    users.append(user)  # replace with db call, making sure to hash the password first
    return signJWT(user.email)


@router.post("/login", tags=["user"])
def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user, users):
        return signJWT(user.email)
    return {"error": "Wrong login details!"}
