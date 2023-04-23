# Om2m - http://192.168.137.185:5089/webpage

from decouple import config
import requests
from fastapi import FastAPI
import json
from pymongo import MongoClient
import time
import threading

Headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/json;ty=4"}


mongoKey = config("mongoKey")
fetchAPI = config("Om2mFetchAPI")


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


def SensorData(freq=1, datathreshold=1000):
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
            # print(sensors)
            sensorIds = getSensorID(sensors)

            for i in sensors:
                if collection.count_documents({"sensorType": i}) == 0:
                    collection.insert_one(
                        {
                            "sensorType": i,
                            "data": sensorData[i],
                            "sensorID": sensorIds[i],
                        }
                    )
                else:
                    # append the data to the existing sensor type
                    currData = collection.find_one({"sensorType": i})["data"]
                    # print(currData, type(currData))
                    currData.extend(sensorData[i])
                    collection.update_one(
                        {"sensorType": i}, {"$set": {"data": currData}}
                    )

            for i in sensors:
                data = collection.find_one({"sensorType": i})["data"]
                if len(data) > datathreshold:
                    data = data[-datathreshold:]
                collection.update_one(
                    {"_id": collection.find_one({"sensorType": i})["_id"]},
                    {"$set": {"data": data}},
                )

        else:
            print("Error: ", res.status_code)
        time.sleep(freq)


if __name__ == "__main__":
    SensorData()
