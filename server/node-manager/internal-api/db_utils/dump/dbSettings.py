import pymongo
from bson.json_util import dumps
from decouple import config

mongokey = config("mongoKey")


# UserDB ->  Collection: UserCollection

# #  'schema': {
#                     'developerId': 'string',
#                     'developerName': 'string',
#                     'Role':  ['AppAdmin', 'AppDeveloper', 'PlatformAdmin'],
#                     'email': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
#                     'password': 'string',
#                     'ApiIds': 'string'
#                 }


# create the above collections in the UserDB with the above schema

DBname = "UserDB"
collectionName = "UserCollection"
schema = {
    "developerId": {"bsonType": "string"},
    "developerName": {"bsonType": "string"},
    "Role": {"enum": ["AppAdmin", "AppDeveloper", "PlatformAdmin"]},
    "email": {
        "bsonType": "string",
        "pattern": "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$",
    },
    "password": {"bsonType": "string"},
    "ApiIds": {"bsonType": "array", "items": {"bsonType": "string"}},
}

client = pymongo.MongoClient(mongokey)
db = client[DBname]
collection = db[collectionName]
collection.create_index([("developerId", pymongo.ASCENDING)], unique=True)
collection.create_index([("email", pymongo.ASCENDING)], unique=True)
collection.create_index([("developerName", pymongo.ASCENDING)], unique=True)
collection.create_index([("ApiIds", pymongo.ASCENDING)], unique=True)
collection.create_index([("Role", pymongo.ASCENDING)], unique=True)
collection.create_index([("password", pymongo.ASCENDING)], unique=True)

# push the schema to the collection
collection.create_collection()
collection.create_validator(schema)
#
