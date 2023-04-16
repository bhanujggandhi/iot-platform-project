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
    response = {"status": 400, "msg": message}
    key = ""
    produce.push(target, key, json.dumps(response))


def utilise_message(t, value):
    value = json.loads(value)
    # try to fetch the data from value if not found then return error
    target, sensorid, fetchType, startTime, endTime, duration = None, None, None, None, None, None
    try:
        target = value['src']
        sensorid = value['sensorid']
        fetchType = value['fetchType']
        startTime = value['startTime']
        endTime = value['endTime']
        duration = value['duration']
    except:
        error_message = "Invalid Request"
        produceError(target, error_message)
        return

    client = MongoClient(mongoKey)
    db = client.SensorDB
    collection = db.SensorData
    sensor_data = []
    error_message = ""
    fetchType = fetchType.lower()
    if fetchType == "timeseries":
        if collection.count_documents({"sensorid": sensorid}) == 0:
            error_message = "Invalid sensorid/No Data Found"
            produceError(target, error_message)
            return
        if startTime == None or endTime == None:
            error_message = "Invalid startTime/endTime"
            produceError(target, error_message)
            return
        if type(startTime) != int or type(endTime) != int:
            error_message = "Invalid startTime/endTime"
            produceError(target, error_message)
            return
        if startTime > endTime:
            error_message = "startTime should be less than endTime"
            produceError(target, error_message)
            return

        data = collection.find({"sensorid": sensorid})
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

    elif fetchType == "realtime":
        realTimeData = []
        if collection.count_documents({"sensorid": sensorid}) == 0:
            error_message = "Invalid sensorid/No Data Found"
            produceError(target, error_message)
            return
        if duration == None or type(duration) != int:
            error_message = "Invalid duration"
            produceError(target, error_message)
            return

        while (duration):
            data = collection.find({"sensorid": sensorid})
            for cur in data:
                cur = cur["data"][-1]
                # timestamp = int(cur[1:-1].split(",")[0])
                realTimeData.append(cur)
                duration -= 1
                time.sleep(1)
        sensor_data = realTimeData

    elif fetchType == "instant":
        insData = []
        if collection.count_documents({"sensorid": sensorid}) == 0:
            error_message = "Invalid sensorid/No Data Found"
            produceError(target, error_message)
            return
        data = collection.find({"sensorid": sensorid})
        for cur in data:
            cur = cur["data"][-1]
            insData.append(cur)
        sensor_data = insData

    response = {"data": sensor_data, "src": "topic_sensor_manager"}
    # produce = Produce()
    key = ""
    produce.push(target, key, json.dumps(response))


TOPIC = 'topic_sensor_manager'
consume = Consume(TOPIC)
while True:
    print('Consuming requests...')
    resp = consume.pull()
    if resp['status'] == False:
        print(resp['value'])
    else:
        print("", resp['value'])
        utilise_message(resp['key'], resp['value'])
    # resp = consume.pull()
    # if resp['status'] == False:
    #     print(resp['value'])
    # else:
    #     print("", resp['value'])
    #     utilise_message(resp['key'], resp['value'])
