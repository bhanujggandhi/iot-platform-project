import pymongo

# from decouple import config

# Set up a MongoDB client
# mongoKey = config('mongoKey')
client = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
)

# # Define a list of databases and collections to create
# dbs_and_collections = [
#     {
#         'db_name': 'UserDB',
#         'collections': [
#             {
#                 'name': 'UserCollection',
#                 'schema': {
#                     'developerId': {'bsonType': 'string'},
#                     'developerName': {'bsonType': 'string'},
#                     'Role': {'enum': ['AppAdmin', 'AppDeveloper', 'PlatformAdmin']},
#                     'email': {'bsonType': 'string', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'},
#                     'password': {'bsonType': 'string'},
#                     'ApiIds': {'bsonType': 'array', 'items': {'bsonType': 'string'}}
#                 }
#             },
#             {
#                 'name': 'AppCollection',
#                 'schema': {
#                     'AppId': {'bsonType': 'string'},
#                     'AppName': {'bsonType': 'string'},
#                     'Services': {'bsonType': 'array', 'items': {'bsonType': 'string'}},
#                     # SENSOR TYPE CAN BE ENUM
#                     'Sensors': {'bsonType': 'array', 'items': {'bsonType': 'string'}},
#                     'Users': {'bsonType': 'array', 'items': {'bsonType': 'string'}},
#                     'Version': {'bsonType': 'double'}
#                 }
#             },
#             {
#                 'name': 'ApiCollection',
#                 'schema': {
#                     'ApiKey': {'bsonType': 'string'},
#                     'developerId': {'bsonType': 'string'}
#                 }
#             },
#             {
#                 'name': 'TrafficCollection',
#                 'schema': {
#                     'ApiKey': {'bsonType': 'string'},
#                     'Api': {'bsonType': 'string'},
#                     'inputParmas': {'bsonType': 'array', 'items': {
#                         'bsonType': 'oneOf',
#                         'oneOf': [
#                             {'bsonType': 'string'},
#                             {'bsonType': 'int'},
#                             {'bsonType': 'double'}
#                         ]
#                     }},
#                 }
#             }
#         ]
#     }

userCollectionSchema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "developerId",
            "developerName",
            "Role",
            "email",
            "password",
            "Appids",
        ],
        "properties": {
            "developerId": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "developerName": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "Role": {
                "enum": ["AppAdmin", "AppDeveloper", "PlatformAdmin"],
                "description": "can only be one of the enum values and is required",
            },
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "Appids": {
                "bsonType": "array",
                "description": "must be an array and is required",
                "items": {
                    "bsonType": "string",
                    "description": "must be a string if the field is present",
                },
            },
        },
    }
}
db = client["ActiveNodeDB"]

# collection = db.create_collection("userCollection", validator=uservalidator)
# modify the validator for the userCollection collection
# userCollection = db.userCollection
# userCollection.drop()
# userCollection = db.create_collection(
#     "userCollection", validator=userCollectionSchema)

# # collection = db.userCollection
# # collection = db.userDB
# print("Insering One :")
# userCollection.insert_one({
#     "developerId": "1234",
#     "developerName": "Vaibhav",
#     "Role": "AppAdmin",
#     'email': "vaibhav.work07@gmaik.com",
#     'password': "123456",
#     'Appids': ["12", "321"]
# })

ActiveNodeScema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["VMid", "IP", "Port", "CPU", "Memory", "OtherStats"],
        "properties": {
            "VMid": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "IP": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "Port": {"bsonType": "int", "description": "must be a int and is required"},
            "CPU": {"bsonType": "int", "description": "must be a int and is required"},
            "Memory": {
                "bsonType": "int",
                "description": "must be a int and is required",
            },
            "OtherStats": {
                "bsonType": "array",
                "description": "must be an array and is required",
                "items": {
                    "bsonType": "string",
                    "description": "must be a string if the field is present",
                },
            },
        },
    }
}


activeNodeCollection = db.create_collection(
    "activeNodeCollection", validator=ActiveNodeScema
)

print("Inserting One :")
activeNodeCollection.insert_one(
    {
        "VMid": "1234",
        "IP": "192.168.172.134",
        "Port": 1234,
        "CPU": 12,
        "Memory": 123,
        "OtherStats": ["12", "321"],
    }
)
