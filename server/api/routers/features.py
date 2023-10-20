import json
import sys
from typing import Annotated

import requests
from bson import ObjectId
from decouple import config
from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from utils.jwt_bearer import JWTBearer
from utils.jwt_handler import decodeJWT
from utils.Messenger import Produce

sys.path.append("..")

router = APIRouter()
produce = Produce()


CONTAINER_NAME = config("deploy_app_container_name")
mongokey = config("mongoKey")
client = MongoClient(mongokey)
db = client["platform"]
app_collection = db.App
user_collection = db.User
service_collection = db.Service

sensor_db = client["SensorDB"]
metadata_collection = sensor_db.SensorMetadata


# ===================================
# Database decoding utility


def sensor_helper_read(sensor) -> dict:
    return {
        # "id": str(sensor["_id"]),
        "sensorid": sensor["sensorid"],
        "sensorName": sensor["sensorName"],
        "sensorType": sensor["sensorType"],
        "sensorLocation": sensor["sensorLocation"],
        "sensorDescription": sensor["sensorDescription"],
    }


# ===================================


@router.get("/sensor/data")
async def get_sensor_data(duration: int):
    node_data = service_collection.find_one({"name": "sensor-manager"})
    res = requests.get(
        f"http://{node_data['ip']}:{node_data['port']}/fetch?sensorID=27785ce4-f175-4f48-8e46-db42f4671f4e&fetchType=RealTime&duration={duration}"
    )

    return {"status": "200", "data": res.text}


@router.get("/sensor/all")
async def get_sensors():
    sensors = []
    for x in metadata_collection.find({}):
        print(x.keys())
        sensors.append(sensor_helper_read(x))

    return {"status": "200", "data": sensors}
