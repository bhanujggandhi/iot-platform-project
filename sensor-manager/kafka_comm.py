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


def utilise_message(target, value):
    value = json.loads(value)
    sensorID, fetchType, duration, startTime, endTime = value["sensorID"], value["fetchType"], value["duration"], value["startTime"], value["endTime"]
    
    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorData
    sensor_data = []

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

        sensor_data = timeSeriesData
    elif fetchType == "RealTime":
        realTimeData = []
        while (duration):
            data = collection.find({"sensorID": sensorID})
            for cur in data:
                cur = cur["data"][-1]
                # timestamp = int(cur[1:-1].split(",")[0])
                realTimeData.append(cur)
                duration -= 1
                time.sleep(1)

        sensor_data = realTimeData

    response = {"data" : sensor_data}
    produce = Produce()
    key = 'topic_sensor_manager'
    produce.push(target, key, json.dumps(response))


TOPIC = 'topic_sensor_manager'
consume = Consume(TOPIC)
while True :
    print('Consuming requests...')
    resp = consume.pull()
    if resp['status'] == False :
        print(resp['value'])
    else :
        utilise_message(resp['key'], resp['value'])