
import requests
from fastapi import FastAPI
import json
from fastapi import APIRouter
from pymongo import MongoClient
import uuid

fetchAPI = "http://127.0.0.1:5089/~/in-cse/in-name/AE-DEV/Device-1/Data?rcn=4"
Headers = {'X-M2M-Origin': 'admin:admin',
           'Content-Type': 'application/json;ty=4'}

mongoKey = ""
# get MongoDB key from config file
with open('config.ini') as f:
    config = json.load(f)
    mongoKey = config['mongoKey']


app = FastAPI()


@app.get("/fetch")
async def fetch(sensorID: str = "", fetchType: str = "", startTime: str = None, endTime: str = None):
    """
    This function will be responsible for fetching the data from Om2m and sending the data to ReqstManager upon request from sensorManager.
    2 Modes of Fetching data from Om2m:
    1.TimeSeries Data
    2.RealTime Stream
    """
    res = requests.get(fetchAPI, headers=Headers)
    if res.status_code == 200:
        return res.json()
    else:
        return {"error": res.status_code}


@app.post("/register")
async def register(sensorName: str = "", sensorType: str = "", sensorLocation: str = "", sensorDescription: str = ""):
    """
    This function will be responsible for registering the sensor with the SensorDB and sending the sensorID to the ReqstManager.
    """
    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorMetadata
    sensorID = str(uuid.uuid4())
    sensor = {"sensorID": sensorID, "sensorName": sensorName, "sensorType": sensorType, "sensorLocation": sensorLocation,
              "sensorDescription": sensorDescription}
    collection.insert_one(sensor)
    return {"sensorID": sensorID}

# bind api to retrive sensor ID from any or all of the sensor metadata
# if more than one sensor metadata is provided, the api will return the sensor ID of any one of the sensors that matches the metadata


@app.get("/bind")
async def bind(sensorName: str = None, sensorType: str = None, sensorLocation: str = None, sensorDescription: str = None):
    """
    This function will be responsible for binding the sensor with the SensorDB and sending the sensorID to the ReqstManager.
    """
    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorMetadata
    sensor = {}
    if sensorName is not None:
        sensor["sensorName"] = sensorName
    if sensorType is not None:
        sensor["sensorType"] = sensorType
    if sensorLocation is not None:
        sensor["sensorLocation"] = sensorLocation
    if sensorDescription is not None:
        sensor["sensorDescription"] = sensorDescription
    if len(sensor) == 0:
        return {"error": "No metadata provided"}
    sensor = collection.find_one(sensor)
    if sensor is None:
        return {"error": "No sensor found"}
    return {"sensorID": sensor["sensorID"]}


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
