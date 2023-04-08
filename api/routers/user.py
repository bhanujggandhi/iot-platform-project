import sys

from fastapi import APIRouter, Body
from utils.model import UserLoginSchema, UserSchema
from utils.jwt_handler import signJWT
from utils.validate import check_user

router = APIRouter()

sys.path.append("..")

users = []


@router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/all")
async def all_users():
    return users


@router.post("/signup")
def create_user(user: UserSchema = Body(...)):
    users.append(user)  # replace with db call, making sure to hash the password first
    return signJWT(user.email)


@router.post("/login")
def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user, users):
        return signJWT(user.email)
    return {"error": "Wrong login details!"}
