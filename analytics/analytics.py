from decouple import config
from pymongo import MongoClient
from bson.objectid import ObjectId
import time
from Messenger import Consume, Produce
from threading import Thread
from time import sleep
import json

mongokey = config("mongoKey")
client = MongoClient(mongokey)

user_db = client["userDB"]
user_collection = user_db.userCollection
app_collection = user_db.AppCollection

sensor_db = client["SensorDB"]
sensor_meta_collection = sensor_db.SensorMetadata

# fetching developer id from the session
developer_id = "6432c7e9b222f4cb5c71cf18"


# fetching id's of developer apps
def get_apps(developer_id):
    query = {"_id": ObjectId(developer_id)}
    developer_app_ids = user_collection.find_one(query)["apps"]
    return developer_app_ids


# fetching type of sensors for each app
def get_sensor_types(app_id):
    query = {"AppId": app_id}
    sensor_types = app_collection.find_one(query)["Sensors"]
    return sensor_types


# fetching sensor id's of each sensor type
def get_sensor_ids(sensor_type):
    query = {"sensorType": sensor_type}
    results = sensor_meta_collection.find(query)
    sensor_ids = [result["sensorID"] for result in results]
    return sensor_ids


def get_start_end_epoch_time(time_period):
    start_time = int(time.time()) - 60 * time_period
    end_time = int(time.time())

    return start_time, end_time


developer_app_ids = get_apps(developer_id)
print(developer_app_ids)

for app_id in developer_app_ids:
    sensor_types = get_sensor_types(app_id)
    print(sensor_types)
    for sensor_type in sensor_types:
        sensor_ids = get_sensor_ids(sensor_type)
        for sensor_id in sensor_ids:
            start_time, end_time = get_start_end_epoch_time(5)

            start_time = 1681053726
            end_time = 1681053767

            request = {
                "sensorID": sensor_id,
                "fetchType": "TimeSeries",
                "duration": 1,
                "startTime": start_time,
                "endTime": end_time,
            }

            TOPIC = "topic_sensor_manager"
            produce = Produce()

            key = "topic_analytics"
            produce.push(TOPIC, key, json.dumps(request))

            consume = Consume(key)
            resp = consume.pull()
            if resp["status"] == False:
                print(resp["value"])
            else:
                response = resp["value"]
                response = json.loads(response)

                # sensor data stored here for sensor_id as an array of array, perform analytics on this data
                sensor_data = response["data"]
                print(sensor_data)