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
from Messenger import Consume, Produce
from threading import Thread
from time import sleep

Headers = {'X-M2M-Origin': 'admin:admin',
           'Content-Type': 'application/json;ty=4'}

mongoKey = config('mongoKey')

produce = Produce()


def produceError(target, message):
    response = {"status": 400, "data": message}
    key = ""
    produce.push(target, key, json.dumps(response))

def utilise_message(value):
    value = json.loads(value)

    target, fetchType = None, None
    try:
        target = value['src']
        fetchType = value['fetchType']
    except:
        error_message = "Invalid Request"
        produceError(target, error_message)
        return

    def fetchTimeSeries(sensorid: str, startTime: int, endTime: int):
        try:
            client = MongoClient(mongoKey)
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
        
    def fetchInstant(sensorid: str):
        try:
            client = MongoClient(mongoKey)
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
        
    def fetchRealTime(sensorid: str, duration: int = 1):
        try:
            client = MongoClient(mongoKey)
            db = client.SensorDB
            collection = db.SensorData
            data = collection.find_one({"sensorid": sensorid})
        except:
            return {"status": 400, "data": "Unable to connect to MongoDB"}

        if data != None:
            realTimeData = []

            while(duration):
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
        
        
    if fetchType == "TimeSeries":
        try:
            sensorid = value['sensorid']
            startTime = value['startTime']
            endTime = value['endTime']

            response = fetchTimeSeries(sensorid, startTime, endTime)
            produce.push(target, "", json.dumps(response))
        except:
            error_message = "Invalid Request"
            produceError(target, error_message)
            return
    elif fetchType == "Instant":
        try:
            sensorid = value['sensorid']

            response = fetchInstant(sensorid)
            produce.push(target, "", json.dumps(response))
        except:
            error_message = "Invalid Request"
            produceError(target, error_message)
            return
    elif fetchType == "RealTime":
        try:
            sensorid = value['sensorid']
            duration = value['duration']

            response = fetchRealTime(sensorid, duration)
            produce.push(target, "", json.dumps(response))
        except:
            error_message = "Invalid Request"
            produceError(target, error_message)
            return
        

TOPIC = 'topic_sensor_manager'
consume = Consume(TOPIC)
while True:
    print('Consuming requests...')
    resp = consume.pull()
    if resp['status'] == False:
        print(resp['value'])
    else:
        utilise_message(resp['value'])
