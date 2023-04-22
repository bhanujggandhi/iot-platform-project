import json
import logging
import time
import uuid
import jwt

import requests
from typing import Annotated
from decouple import config
from fastapi import APIRouter, FastAPI, Request, Depends
from utils.jwt_bearer import JWTBearer
from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi.middleware.cors import CORSMiddleware

Headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/json;ty=4"}

mongoKey = config("mongoKey")
fetchAPI = config("Om2mFetchAPI")

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=[""],
)


# -------Helper functions--------
def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token["expiry"] >= time.time() else None
    except:
        return {}


# -------API endpoints--------
@app.get("/fetchSensors", dependencies=[Depends(JWTBearer())])
async def fetchSensors(token: Annotated[str, Depends(JWTBearer())]):
    """
    This function will return all the unique sensor types
    """

    if token == "":
        return {"status": 400, "data": "Invalid parms"}

    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)["id"]
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user["role"] != "developer":
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}

        db = client.SensorDB
        collection = db.SensorMetadata
        cursor = collection.find({}, {"_id": 0})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    sensor_types = set()
    for document in cursor:
        sensor_types.add(document["sensorType"])

    client.close()

    if len(sensor_types) == 0:
        return {"status": 400, "data": "No sensor types found"}
    else:
        return {"status": 200, "data": list(sensor_types)}


@app.get("/fetchSensors/type", dependencies=[Depends(JWTBearer())])
async def fetchSensorsbyType(
    token: Annotated[str, Depends(JWTBearer())], sensorType: str
):
    """
    This function will return all the instances of a particular sensor type
    """

    if token == "" or sensorType == "":
        return {"status": 400, "data": "Invalid parms"}

    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)["id"]
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user["role"] != "developer":
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}

        db = client.SensorDB
        collection = db.SensorMetadata
        cursor = collection.find({"sensorType": sensorType})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    sensor_data = []
    for document in cursor:
        sensor_data.append(document["sensorid"])

    client.close()

    if len(sensor_data) == 0:
        return {"status": 400, "data": "No sensor found"}
    else:
        return {"status": 200, "data": sensor_data}


@app.get("/fetch/TimeSeries", dependencies=[Depends(JWTBearer())])
async def fetchTimeSeries(
    token: Annotated[str, Depends(JWTBearer())],
    sensorid: str,
    startTime: int,
    endTime: int,
):
    """
    This function will return data of a given sensor id from startTime till endTime
    """

    if token == "" or sensorid == "" or startTime == None or endTime == None:
        return {"status": 400, "data": "Invalid parms"}

    # Check whether app is authorized to access sensor : sensorid
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)["id"]
        db = client.platform
        collection = db.App

        _app = collection.find_one({"_id": ObjectId(id)})
        if _app != None:
            if sensorid not in _app["sensorId"]:
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "App not found"}

        # Fetching timeseries sensor data
        db = client.SensorDB
        collection = db.SensorData
        data = collection.find_one({"sensorid": sensorid})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    if data != None:
        timeSeriesData = []
        data = data["data"]
        for datapoint in data:
            timestamp = int(datapoint[1:-1].split(",")[0])
            if (startTime <= timestamp) and (timestamp <= endTime):
                timeSeriesData.append(datapoint)

        if len(timeSeriesData) != 0:
            return {"status": 200, "data": timeSeriesData}
        else:
            return {"status": 400, "data": "No sensor data found"}

    else:
        return {"status": 400, "data": "Sensor id not valid"}


@app.get("/fetch/Instant", dependencies=[Depends(JWTBearer())])
async def fetchInstant(token: Annotated[str, Depends(JWTBearer())], sensorid: str):
    """
    This function will return last datapoint of a given sensor id
    """

    if token == "" or sensorid == "":
        return {"status": 400, "data": "Invalid parms"}

    # Check whether app is authorized to access sensor : sensorid
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)["id"]
        db = client.platform
        collection = db.App

        _app = collection.find_one({"_id": ObjectId(id)})
        if _app != None:
            if sensorid not in _app["sensorId"]:
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "App not found"}

        # Fetching latest instance of sensor data
        db = client.SensorDB
        collection = db.SensorData
        data = collection.find_one({"sensorid": sensorid})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    if data != None:
        instantData = data["data"][-1]

        if len(instantData) != 0:
            return {"status": 200, "data": instantData}
        else:
            return {"status": 400, "data": "No sensor data found"}

    else:
        return {"status": 400, "data": "Sensor id not valid"}


@app.get("/fetch/RealTime", dependencies=[Depends(JWTBearer())])
async def fetchRealTime(
    token: Annotated[str, Depends(JWTBearer())], sensorid: str, duration: int = 1
):
    """
    This function will return realtime data for a given sensor id for a specified duration
    """

    if token == "" or sensorid == "":
        return {"status": 400, "data": "Invalid parms"}

    # Check whether app is authorized to access sensor : sensorid
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)["id"]
        db = client.platform
        collection = db.App

        _app = collection.find_one({"_id": ObjectId(id)})
        if _app != None:
            if sensorid not in _app["sensorId"]:
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "App not found"}

        # Fetching realtime sensor data
        db = client.SensorDB
        collection = db.SensorData
        data = collection.find_one({"sensorid": sensorid})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    if data != None:
        realTimeData = []

        while duration:
            data = collection.find_one({"sensorid": sensorid})["data"]
            realTimeData.append(data[-1])
            duration -= 1
            time.sleep(1)

        if len(realTimeData) != 0:
            return {"status": 200, "data": realTimeData}
        else:
            return {"status": 400, "data": "No sensor data found"}

    else:
        return {"status": 400, "data": "Sensor id not valid"}


@app.post("/register", dependencies=[Depends(JWTBearer())])
async def register(
    token: Annotated[str, Depends(JWTBearer())],
    sensorName: str,
    sensorType: str,
    sensorLocation: str,
    sensorDescription: str = "",
):
    """
    This function will be responsible for registering the sensor with the SensorDB and sending the sensorid to the ReqstManager.
    """

    if sensorName == "" or sensorType == "" or sensorLocation == "":
        return {"status": 400, "data": "Invalid parms"}

    # Do authorization, role must be platform
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)["id"]
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user["role"] != "platform":
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}

        client = MongoClient(mongoKey)
        db = client.SensorDB
        collection = db.SensorMetadata
        sensorid = str(uuid.uuid4())

        sensor = {
            "sensorName": sensorName,
            "sensorType": sensorType,
            "sensorLocation": sensorLocation,
            "sensorDescription": sensorDescription,
            "sensorid": sensorid,
        }

        if collection.find_one({"sensorName": sensorName}) != None:
            return {"status": 400, "data": "Sensor name already exists"}

        collection.insert_one(sensor)
        return {"status": 200, "data": sensorid}
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}


@app.delete("/deregister", dependencies=[Depends(JWTBearer())])
async def deregister(token: Annotated[str, Depends(JWTBearer())], sensorid: str):
    """
    This function will be responsible for deregistering the sensor with the SensorDB and sending the status code to the ReqstManager.
    """

    if sensorid == "":
        return {"status": 400, "data": "Invalid parms"}

    # Do authorization, role must be platform
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)["id"]
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user["role"] != "platform":
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}

        client = MongoClient(mongoKey)
        db = client.SensorDB
        collection = db.SensorMetadata
        data = collection.find_one({"sensorid": sensorid})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    if data != None:
        try:
            sensor = {"sensorid": sensorid}
            collection.delete_one(sensor)
            return {"status": 200, "data": "success"}
        except:
            return {"status": 400, "data": "failure"}
    else:
        return {"status": 400, "data": "Sensor id not valid"}


@app.get("/bind")
async def bind():
    """
    Not applicable right now
    """
    pass
