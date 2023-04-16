
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
import time


Headers = {'X-M2M-Origin': 'admin:admin',
           'Content-Type': 'application/json;ty=4'}

mongoKey = config('mongoKey')
fetchAPI = config('Om2mFetchAPI')


app = FastAPI()


# Configure the logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("sensor_logger.log")
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     try:
#         body = await request.body()
#         body = json.loads(body.decode("utf-8"))
#     except:
#         body = None

#     response = await call_next(request)
#     if response.status_code >= 400:
#         error_message = response.json().get("error") or response.text
#         logger.error(
#             f"{request.method} {request.url.path} - {response.status_code}: {error_message}")
#     else:
#         logger.info(
#             f"{request.method} {request.url.path} - {response.status_code} - {body}")

#     return response


@app.get("/fetch")
async def fetch(sensorID: str = "", fetchType: str = "realtime", duration: int = 1, startTime: int = None, endTime: int = None):
    """
    This function will be responsible for fetching the data from Om2m and sending the data to ReqstManager upon request from sensorManager.
    2 Modes of Fetching data from Om2m:
    1.TimeSeries Data
    2.RealTime Stream
    """
    fetchType = fetchType.lower()
    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorData
    # find all data in DB
    if fetchType == "timeseries":
        if collection.count_documents({"sensorID": sensorID}) == 0:
            return {"Error": 400, "Message": "Invalid SensorID/No Data Found"}
        # using objectID to find
        data = collection.find({"sensorID": sensorID})
        # print(data.explain())
        timeSeriesData = []
        for cur in data:
            # print(cur)
            cur = cur["data"]
            for d in cur:
                # d =  "[1680961091, 1, 117]"  sample
                timestamp = int(d[1:-1].split(",")[0])
                # if timestamp >= startTime and timestamp <= endTime:
                if (startTime <= timestamp) and (timestamp <= endTime):
                    timeSeriesData.append(d)

        return {"data": timeSeriesData}
    elif fetchType == "realtime":
        realTimeData = []
        if collection.count_documents({"sensorID": sensorID}) == 0:
            return {"Error": 400, "Message": "Invalid SensorID/No Data Found"}
        while (duration):

            data = collection.find({"sensorID": sensorID})
            # print(data)
            # check if data is empty
            # check if cursor returned points to a valid document

            for cur in data:
                cur = cur["data"][-1]
                # timestamp = int(cur[1:-1].split(",")[0])
                realTimeData.append(cur)
                duration -= 1
                time.sleep(1)

        return {"data": realTimeData}
    else:
        return {"Error": 400, "Message": "Parms not found"}

        # realTimeData.append(d)
    # res = requests.get(fetchAPI, headers=Headers)
    # if res.status_code == 200:
    #     return res.json()
    # else:
    #     return {"error": res.status_code}


@ app.post("/register")
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

    sensor = {"sensorID": sensorID, "sensorName": sensorName, "sensorType": sensorType, "sensorLocation": sensorLocation,
              "sensorDescription": sensorDescription}
    collection.insert_one(sensor)
    return {"sensorID": sensorID}

# bind api to retrive sensor ID from any or all of the sensor metadata
# if more than one sensor metadata is provided, the api will return the sensor ID of any one of the sensors that matches the metadata


@ app.get("/bind")
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


@ app.delete("/deregister")
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
