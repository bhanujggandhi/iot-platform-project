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
from remotecalls import *

Headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/json;ty=4"}
mongoKey = config("mongoKey")
produce = Produce()


def utilise_message(value):
    value = json.loads(value)
    print(value)

    src = value['src']
    readingtype, lat, long, sensorIDs, starttime, numofsensors, data_flag = '', '', '', [], '', 1, True

    if 'readingtype' in value:
        readingtype = value['readingtype']
    if 'starttime' in value:
        starttime = value['starttime']
    if 'numofsensors' in value:
        numofsensors = value['numofsensors']
    if 'lat' in value:
        lat = value['lat']
    if 'long' in value:
        long = value['long']
    if 'sensorIDs' in value:
        sensorIDs = value['sensorIDs']
    if 'data_flag' in value:
        data_flag = value['data_flag']
    

    parms = {
        "readingtype": readingtype,
        "starttime": starttime,
        "numofsensors": numofsensors,
        "lat": lat,
        "long": long,
        "sensorIDs": sensorIDs,
        "data_flag": data_flag
    }

    response = fetchdata(parms)
    produce.push(src, "", json.dumps(response))


TOPIC = "topic_sensor_manager"
consume = Consume(TOPIC)
while True:
    print("Consuming requests...")
    resp = consume.pull()
    if resp["status"] == False:
        print(resp["value"])
    else:
        utilise_message(resp["value"])
