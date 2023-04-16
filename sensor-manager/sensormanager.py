import json
import logging
import time
import uuid
import jwt

import requests
from decouple import config
from fastapi import APIRouter, FastAPI, Request, Depends
from utils.jwt_bearer import JWTBearer
from pymongo import MongoClient

Headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/json;ty=4"}

mongoKey = config("mongoKey")
fetchAPI = config("Om2mFetchAPI")

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

app = FastAPI()

def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token["expiry"] >= time.time() else None
    except:
        return {}

@app.get("/fetchSensors")
async def fetchSensors():
    """
    This function will return all the unique sensor types
    """

    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorMetadata
    cursor = collection.find({}, {"_id": 0})
    documents = list(cursor)
    client.close()
    return {"status": 200, "data": "We have stopped your app successfully"}
    return {"data" : documents}


@app.get("/fetchSensors/type", dependencies=[Depends(JWTBearer())])
async def fetchSensorsbyType():
    """
    This function will return all the instances of a particular sensor type
    """

    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorMetadata
    cursor = collection.find({}, {"_id": 0})
    documents = list(cursor)
    client.close()
    return {"data" : documents}


@app.get("/fetchTimeSeries")
async def fetchTimeSeries(sensorID: str = "", fetchType: str = "", duration: int = 1, startTime: int = None, endTime: int = None):
    """
    This function will return data of a given sensor id from startTime till endTime
    """

    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorData
    # find all data in DB
    if fetchType == "TimeSeries":
        data = collection.find({"sensorID": sensorID})
        # print(data)
        if data == None:
            return {"data": []}
        timeSeriesData = []
        for cur in data:
            cur = cur["data"]
            for d in cur:
                # d =  "[1680961091, 1, 117]"  sample
                timestamp = int(d[1:-1].split(",")[0])
                # if timestamp >= startTime and timestamp <= endTime:
                if (startTime <= timestamp) and (timestamp <= endTime):
                    timeSeriesData.append(d)

        return {"data": timeSeriesData}
    else:
        return {"Error": 400, "Message": "Parms not found"}
    

@app.get("/fetchInstant")
async def fetchInstant(sensorID: str = "", fetchType: str = "", duration: int = 1, startTime: int = None, endTime: int = None):
    """
    This function will return last datapoint of a given sensor id
    """

    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorData
    # find all data in DB
    if fetchType == "Instant":
        realTimeData = []
        data = collection.find({"sensorID": sensorID})
        if data == None:
            return {"data": []}
        else:
            realTimeData = data[0]["data"][-1]

        return {"data": realTimeData}
    else:
        return {"Error": 400, "Message": "Parms not found"}
    

@app.get("/fetchRealTime")
async def fetchRealTime(sensorID: str = "", fetchType: str = "", duration: int = 1, startTime: int = None, endTime: int = None):
    """
    This function will return realtime data for a given sensor id for a specified duration
    """
    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorData
    # find all data in DB
    if fetchType == "RealTime":
        realTimeData = []
        while duration:
            data = collection.find({"sensorID": sensorID})
            # print(data)
            if data == None:
                return {"data": []}
            for cur in data:
                cur = cur["data"][-1]
                # timestamp = int(cur[1:-1].split(",")[0])
                realTimeData.append(cur)
                duration -= 1
                time.sleep(1)

        return {"data": realTimeData}
    else:
        return {"Error": 400, "Message": "Parms not found"}
    

@app.post("/register")
async def register(sensorName: str = "", sensorType: str = "", sensorLocation: str = "", sensorDescription: str = ""):
    """
    This function will be responsible for registering the sensor with the SensorDB and sending the sensorID to the ReqstManager.
    """

    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorMetadata
    sensorID = str(uuid.uuid4())
    if sensorID == "" or sensorType == "" or sensorLocation == "" or sensorDescription == "":
        return {"Error": 400, "Message": "Parms not found"}

    sensor = {
        "sensorID": sensorID,
        "sensorName": sensorName,
        "sensorType": sensorType,
        "sensorLocation": sensorLocation,
        "sensorDescription": sensorDescription,
    }
    collection.insert_one(sensor)
    return {"sensorID": sensorID}


@app.delete("/deregister")
async def deregister(sensorID: str = ""):
    """
    This function will be responsible for deregistering the sensor with the SensorDB and sending the status code to the ReqstManager.
    """

    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorMetadata
    sensor = {"sensorID": sensorID}
    collection.delete_one(sensor)
    return {"status": "success"}


@app.get("/bind")
async def bind(
    sensorName: str = None, sensorType: str = None, sensorLocation: str = None, sensorDescription: str = None):
    """
    Not applicable right now
    """
    pass