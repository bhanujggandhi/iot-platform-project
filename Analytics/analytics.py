from decouple import config
from pymongo import MongoClient
from bson.objectid import ObjectId

mongokey = config('mongoKey')
client = MongoClient(mongokey)

user_db = client['userDB']
user_collection = user_db.userCollection
app_collection = user_db.AppCollection

sensor_db = client['SensorDB']
sensor_meta_collection = sensor_db.SensorMetadata

#fetching developer id from the session
developer_id = '6432c7e9b222f4cb5c71cf18'

#fetching id's of developer apps
def get_apps(developer_id):
    query = {'_id' : ObjectId(developer_id)}
    developer_app_ids = user_collection.find_one(query)['apps']
    return developer_app_ids

#fetching type of sensors for each app
def get_sensor_types(app_id):
    query = {'AppId' : app_id}
    sensor_types = app_collection.find_one(query)['Sensors']
    return sensor_types


#fetching sensor id's of each sensor type
def get_sensor_ids(sensor_type):
    query = {'sensorType' : sensor_type}
    results = sensor_meta_collection.find(query)
    sensor_ids = [result["sensorID"] for result in results]
    return sensor_ids

developer_app_ids = get_apps(developer_id)
print(developer_app_ids)

for app_id in developer_app_ids:
    sensor_types = get_sensor_types(app_id)
    print(sensor_types)
    for sensor_type in sensor_types:
        sensor_ids = get_sensor_ids(sensor_type)
        print(sensor_ids)