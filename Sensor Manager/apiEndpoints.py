
import requests
from fastapi import FastAPI
import json
from fastapi import APIRouter
from pymongo import MongoClient
import uuid
from decouple import config
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel


Headers = {'X-M2M-Origin': 'admin:admin',
           'Content-Type': 'application/json;ty=4'}

mongoKey = config('mongoKey')
fetchAPI = config('Om2mFetchAPI')


app = FastAPI()


# Configure the logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("sensor_logger.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        body = await request.body()
        body = json.loads(body.decode("utf-8"))
        print(body)
    except:
        body = None
    response = await call_next(request)
    if response.status_code >= 400:
        error_message = response.json().get("error") or response.text
        logger.error(f"{request.method} {request.url.path} - {response.status_code}: {error_message}")
    else:
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {body}")
        
    return await call_next(request)



@app.get("/fetch")
async def fetch(sensorID: str = "", fetchType: str = "", startTime: int = None, endTime: int = None):
    """
    This function will be responsible for fetching the data from Om2m and sending the data to ReqstManager upon request from sensorManager.
    2 Modes of Fetching data from Om2m:
    1.TimeSeries Data
    2.RealTime Stream
    """
    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorData
    # find all data in DB
    if fetchType == "TimeSeries":
        data = collection.find({"sensorID": sensorID})
        timeSeriesData = []
        for cur in data:
            cur = cur["data"]
            for d in cur:
                # d =  "[1680961091, 1, 117]"  sample
                timestamp = int(d[1:-1].split(",")[0])
                # if timestamp >= startTime and timestamp <= endTime:
                if (startTime <= timestamp) and (timestamp <= endTime):
                    timeSeriesData.append(d)

        return timeSeriesData

    # res = requests.get(fetchAPI, headers=Headers)
    # if res.status_code == 200:
    #     return res.json()
    # else:
    #     return {"error": res.status_code}


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
async def bind(devId: str = None, sensorName: str = None, sensorType: str = None, sensorLocation: str = None, sensorDescription: str = None):
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


# @app.
