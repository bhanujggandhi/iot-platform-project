import json
import logging
import time
import uuid

import requests
import uvicorn
from fastapi import APIRouter, FastAPI, Request
from pymongo import MongoClient

Headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/json;ty=4"}

mongoKey = "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
fetchAPI = "http://192.168.154.246:5089/~/in-cse/in-name/AE-DEV/Device-2/Data?rcn=4"


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
    except:
        body = None

    response = await call_next(request)
    if response.status_code >= 400:
        error_message = response.json().get("error") or response.text
        logger.error(
            f"{request.method} {request.url.path} - {response.status_code}: {error_message}"
        )
    else:
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {body}"
        )

    return response


@app.get("/fetch")
async def fetch(
    sensorID: str = "",
    fetchType: str = "",
    duration: int = 1,
    startTime: int = None,
    endTime: int = None,
):
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
    elif fetchType == "RealTime":
        realTimeData = []
        while duration:
            data = collection.find({"sensorID": sensorID})
            if data == None:
                return {"data": []}
            for cur in data:
                cur = cur["data"][-1]
                # timestamp = int(cur[1:-1].split(",")[0])
                realTimeData.append(cur)
                duration -= 1
                time.sleep(1)

        return {"data": realTimeData}

        # realTimeData.append(d)
    # res = requests.get(fetchAPI, headers=Headers)
    # if res.status_code == 200:
    #     return res.json()
    # else:
    #     return {"error": res.status_code}


@app.post("/register")
async def register(
    sensorName: str = "",
    sensorType: str = "",
    sensorLocation: str = "",
    sensorDescription: str = "",
):
    """
    This function will be responsible for registering the sensor with the SensorDB and sending the sensorID to the ReqstManager.
    """
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
    return {"sensorID": sensorID}


# bind api to retrive sensor ID from any or all of the sensor metadata
# if more than one sensor metadata is provided, the api will return the sensor ID of any one of the sensors that matches the metadata


@app.get("/bind")
async def bind(
    devId: str = None,
    sensorName: str = None,
    sensorType: str = None,
    sensorLocation: str = None,
    sensorDescription: str = None,
):
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info", port=80)
