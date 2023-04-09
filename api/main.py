import asyncio
import os
import shutil
import sys
from typing import List, Union

import uvicorn
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import deployement, tasks, user
from utils.jwt_handler import decodeJWT, signJWT

sys.path.append("..")

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
app.include_router(deployement.router, prefix="/deploy", tags=["deployement"])
# app.include_router(tasks.router)


@app.get("/", tags=["test"])
async def read_root():
    return {"Hello": "World"}


@app.get("/apitoken/generate/{userid}", tags=["auth"])
async def generate_token(userid: str):
    return signJWT(userid)


@app.get("/apitoken/verify/{token}", tags=["auth"])
async def verify_token(token: str):
    return decodeJWT(token)
