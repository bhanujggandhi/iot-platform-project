from pymongo import MongoClient
import schema
from decouple import config
from schema import *

mongoKey = config("mongoKey")

client = MongoClient(mongoKey)

dbs = {
    # "userDB": ["userCollection", "ApiCollection", "AppCollection", "TrafficCollection"],
    "ActiveNodeDB": ["activeNodeCollection"],
    # "SensorDB": ["SensorData", "SensorMetadata"],
    "platform": ["Module_Status"],
}

for db in dbs.keys():
    create_db = client[db]
    for collection in dbs[db]:
        if collection not in create_db.list_collection_names():
            var = collection + "Schema"
            collectionschema = getattr(schema, var)
            print(collection)
            new_collection = create_db.create_collection(
                name=collection, validator=collectionschema["validator"]
            )
