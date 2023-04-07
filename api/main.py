import os
import shutil
from typing import Union
import uvicorn

from utils.jwt_bearer import JWTBearer
from utils.jwt_handler import decodeJWT, signJWT
from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, status
from utils.verify_zip import verify_zip

from routers import users, deployement

app = FastAPI()

app.include_router(users.router, prefix="/users")
app.include_router(deployement.router, prefix="/deploy")


@app.get("/", tags=["test"])
async def read_root():
    return {"Hello": "World"}


@app.get("/apitoken/generate/{userid}", tags=["auth"])
async def generate_token(userid: str):
    return signJWT(userid)


@app.get("/apitoken/verify/{token}", tags=["auth"])
async def verify_token(token: str):
    return decodeJWT(token)
