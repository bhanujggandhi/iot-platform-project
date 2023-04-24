import asyncio
import os
import shutil
import sys
from typing import List, Union
import time

import uvicorn
from beanie import init_beanie
from decouple import config
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from routers import deployment, user, apps, features, analytics
from utils.jwt_handler import decodeJWT, signJWT

MONGO_URI = config("mongoKey")


app = FastAPI(
    title="Internal APIs",
    description="This API module contains all the platform's internal APIs that will be required by platform to work",
    docs_url="/",
)

origins = [
    "0.0.0.0",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(features.router, prefix="/features", tags=["Platform Features"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


@app.get("/", tags=["test"])
async def monitoring_test():
    return {"name": "internal-api"}


@app.get("/ping/internal-api", tags=["test"])
async def monitoring_test():
    return {"name": "internal-api", "data": {"timestamp": time.time()}}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", log_level="info", port=5000, workers=4, reload=True
    )
