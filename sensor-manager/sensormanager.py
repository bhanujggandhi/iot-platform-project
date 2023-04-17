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
    try:
        client = MongoClient(mongoKey)
        db = client.SensorDB
        collection = db.SensorMetadata
        cursor = collection.find({}, {"_id": 0})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    sensor_types = set()
    for document in cursor:
        sensor_types.add(document['sensorType'])

    client.close()
    
    if len(sensor_types) == 0:
        return {"status": 400, "data": "No sensor types found"}
    else:
        return {"status": 200, "data": list(sensor_types)}


@app.get("/fetchSensors/type", dependencies=[Depends(JWTBearer())])
async def fetchSensorsbyType(token: Annotated[str, Depends(JWTBearer())], sensor_type : str):
    """
    This function will return all the instances of a particular sensor type
    """

    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)['id']
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user['role'] != 'developer':
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}

        
        db = client.SensorDB
        collection = db.SensorMetadata
        cursor = collection.find({"sensorType" : sensor_type})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    sensor_data = []
    for document in cursor:
        sensor_data.append(document['sensorid'])

    client.close()

    if len(sensor_data) == 0:
        return {"status": 400, "data": "No sensor found"}
    else:
        return {"status": 200, "data": sensor_data}


@app.get("/fetch/TimeSeries", dependencies=[Depends(JWTBearer())])
async def fetchTimeSeries(token: Annotated[str, Depends(JWTBearer())], sensorID: str, startTime: int, endTime: int):
    """
    This function will return data of a given sensor id from startTime till endTime
    """

    # Do authorization, app id to sensor id
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)['id']
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user['role'] != 'developer':
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}


        # Fetching timeseries sensor data
        db = client.SensorDB
        collection = db.SensorData
        data = collection.find_one({"sensorid": sensorID})
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
async def fetchInstant(token: Annotated[str, Depends(JWTBearer())], sensorID: str):
    """
    This function will return last datapoint of a given sensor id
    """

    # Do authorization, app id to sensor id
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)['id']
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user['role'] != 'developer':
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}
    

        # Fetching latest instance of sensor data
        db = client.SensorDB
        collection = db.SensorData
        data = collection.find_one({"sensorid": sensorID})
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
async def fetchRealTime(token: Annotated[str, Depends(JWTBearer())], sensorID: str, duration: int = 1):
    """
    This function will return realtime data for a given sensor id for a specified duration
    """

    # Do authorization, app id to sensor id
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)['id']
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user['role'] != 'developer':
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}
        
        
        # Fetching realtime sensor data
        db = client.SensorDB
        collection = db.SensorData
        data = collection.find_one({"sensorid": sensorID})
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}

    if data != None:
        realTimeData = []

        while(duration):
            data = collection.find_one({"sensorid": sensorID})["data"]
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
async def register(token: Annotated[str, Depends(JWTBearer())], sensorName: str, sensorType: str, sensorLocation: str, sensorDescription: str = ""):
    """
    This function will be responsible for registering the sensor with the SensorDB and sending the sensorID to the ReqstManager.
    """

    if sensorName == "" or sensorType == "" or sensorLocation == "":
        return {"status": 400, "data": "Invalid parms"}

    # Do authorization, role must be platform
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)['id']
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user['role'] != 'platform':
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}


        client = MongoClient(mongoKey)
        db = client.SensorDB
        collection = db.SensorMetadata
        sensorID = str(uuid.uuid4())
    
        sensor = {
            "sensorID": sensorID,
            "sensorName": sensorName,
            "sensorType": sensorType,
            "sensorLocation": sensorLocation,
            "sensorDescription": sensorDescription,
        }

        collection.insert_one(sensor)
        return {"status": 200, "data": sensorID}
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}


@app.delete("/deregister", dependencies=[Depends(JWTBearer())])
async def deregister(token: Annotated[str, Depends(JWTBearer())], sensorID: str):
    """
    This function will be responsible for deregistering the sensor with the SensorDB and sending the status code to the ReqstManager.
    """

    if sensorID == "":
        return {"status": 400, "data": "Invalid parms"}
    
    # Do authorization, role must be platform
    try:
        client = MongoClient(mongoKey)
        id = decodeJWT(token)['id']
        db = client.platform
        collection = db.User

        user = collection.find_one({"_id": ObjectId(id)})
        if user != None:
            if user['role'] != 'platform':
                return {"status": 400, "data": "Not authorized"}
        else:
            return {"status": 400, "data": "User not found"}

        client = MongoClient(mongoKey)
        db = client.SensorDB
        collection = db.SensorMetadata
        data = collection.find_one({"sensorid": sensorID})        
    except:
        return {"status": 400, "data": "Unable to connect to MongoDB"}
    
    if data != None:
        try:
            sensor = {"sensorid": sensorID}
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