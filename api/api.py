import os
import shutil
from typing import Union, List

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routers import deployement, user, tasks
from scheduler import app as scheduler_app
from utils.jwt_bearer import JWTBearer
from utils.jwt_handler import decodeJWT, signJWT
from utils.verify_zip import verify_zip
from utils.model import Task

app = FastAPI(
    title="Internal APIs",
    description="This API module contains all the platform's internal APIs that will be required by platform to work",
)


"""
Enable CORS so that the React application can communicate with FastAPI. 

Need modify these when in production.
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session = scheduler_app.session


app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(deployement.router, prefix="/deploy", tags=["deployement"])
app.include_router(tasks.router)


@app.get("/", tags=["test"])
async def read_root():
    return {"Hello": "World"}


@app.get("/apitoken/generate/{userid}", tags=["auth"])
async def generate_token(userid: str):
    return signJWT(userid)


@app.get("/apitoken/verify/{token}", tags=["auth"])
async def verify_token(token: str):
    return decodeJWT(token)
