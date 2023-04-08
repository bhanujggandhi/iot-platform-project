# Om2m - http://192.168.137.185:5089/webpage

import requests
from fastapi import FastAPI
import json
from pymongo import MongoClient
import time
import threading
fetchAPI = "http://192.168.154.246:5089/~/in-cse/in-name/AE-DEV/Device-1/Data?rcn=4"
Headers = {'X-M2M-Origin': 'admin:admin',
           'Content-Type': 'application/json;ty=4'}

mongoKey = ""
# get MongoDB key from config file
with open('config.ini') as f:
    config = json.load(f)
    mongoKey = config['mongoKey']


def processData(data):
    """
    process the data received from om2m and separate the data into different sensor types
    """
    # make a dictionary of sensor types and their corresponding data
    sensorData = {}
    data = data["m2m:cnt"]["m2m:cin"]
    for i in data:
        sensorlabels = i["lbl"]
        con = i["con"]
        for j in sensorlabels:
            if j not in sensorData:
                sensorData[j] = []
            sensorData[j].append(con)
    return sensorData


def getSensorID(sensorLabels):
    sensorIDs = {}
    for i in sensorLabels:
        client = MongoClient(mongoKey)
        db = client.SensorDB
        collection = db.SensorMetadata
        sensorIDs[i] = collection.find_one({"sensorName": i})["sensorID"]
    return sensorIDs


def SensorData(freq=10, datathreshold=50):
    # This function will be responsible for fetching the data from Om2m and sending the data to MongoDB for storage.
    # when 50 instances of a particular sensor type are stored in the database, the oldest instance will be deleted
    # to make space for the new instance
    # run in every 10 seconds
    while True:
        res = requests.get(fetchAPI, headers=Headers)
        if res.status_code == 200:
            data = res.json()
            sensorData = processData(data)
            client = MongoClient(mongoKey)
            db = client.SensorDB
            collection = db.SensorData
            sensors = sensorData.keys()
            sensorIds = getSensorID(sensors)

            # check if count of documents with a particular sensor type is if 50, delete the the oldest 10 documents where the first entry in data is timestamp

            for i in sensors:
                if collection.count_documents({"sensorType": i}) >= 50:
                    collection.delete_many(
                        {"sensorType": i}, limit=50)

            for i in sensors:
                if collection.count_documents({"sensorType": i}) == 0:
                    collection.insert_one(
                        {"sensorType": i, "data": sensorData[i], "sensorID": sensorIds[i]})
                else:
                    # append the data to the existing sensor type
                    currData = collection.find_one(
                        {"sensorType": i})["data"]
                    # print(currData, type(currData))
                    currData.extend(sensorData[i])
                    collection.update_one({"sensorType": i}, {
                        "$set": {"data": currData}})

            for i in sensors:
                data = collection.find_one({"sensorType": i})["data"]
                if len(data) > datathreshold:
                    data = data[-datathreshold:]
                collection.update_one({'_id': collection.find_one(
                    {"sensorType": i})['_id']}, {'$set': {'data': data}})

        else:
            print("Error: ", res.status_code)
        time.sleep(freq)


def SensorManager():
    """
    This function will be responsible for processing API requests received from the RqstManager and
    sending the appropriate response back to the RqstManager.

    For Processing API requests, the SensorManager will after Verification of the request, send the request to the
    SensorStream and sensor Stream will process the request and send the response back to the ReqstManager.
    """
    pass


def ReqstManager():
    """
    This function will be endpoint for all the API requests received from the client , it will redirect the request to the
    SensorManager for processing and will send the response back to the client.
    """
    # create a server listening for requests


def SensorStream():
    """
    This function will be responsible for fetching the data from Om2m and sending the data to ReqstManager upon request from sensorManager.
    2 Modes of Fetching data from Om2m:
    1.TimeSeries Data
    2.RealTime Stream
    """
    pass


def Validator():
    """
    This function will be responsible for validating the Sensor metadata  from SensorDB and respond the correctness of Sensor metadata.
    """
    pass


def LogManager():
    """
    This function will be responsible for logging all the requests received from the client and the responses staus Codes sent back to the client.
    """
    pass


if __name__ == "__main__":
    SensorData()
