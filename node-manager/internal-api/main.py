import asyncio
import os
import shutil
import sys
from typing import List, Union

import uvicorn
from beanie import init_beanie
from decouple import config
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from routers import deployment, user, apps
from utils.jwt_handler import decodeJWT, signJWT

MONGO_URI = config("mongoKey")


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


app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(deployment.router, prefix="/deploy", tags=["deployement"])
app.include_router(apps.router, prefix="/apps", tags=["Deployed App"])


@app.get("/", tags=["test"])
async def read_root():
    return {"Hello": "World"}


@app.get("/apitoken/generate/{userid}", tags=["auth"])
async def generate_token(userid: str):
    return signJWT(userid)


@app.get("/apitoken/verify/{token}", tags=["auth"])
async def verify_token(token: str):
    return decodeJWT(token)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info", port=80, workers=4, reload=True)
