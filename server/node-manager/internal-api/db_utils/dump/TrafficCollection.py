import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
)

schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "title": "Student Object Validation",
            "required": ["ApiKey", "Api"],
            "properties": {
                "ApiKey": {"bsonType": "string"},
                "Api": {"bsonType": "string"},
                "InputParams": {
                    "bsonType": "array",
                    "items": {
                        "oneOf": [
                            {"bsonType": "string"},
                            {"bsonType": "int"},
                            {"bsonType": "date"},
                            {"bsonType": "bool"},
                            {"bsonType": "double"},
                            {"bsonType": "objectId"},
                        ]
                    },
                },
                "Status": {"bsonType": "int"},
                "StartTime": {"bsonType": "timestamp"},
                "EndTime": {"bsonType": "timestamp"},
            },
        }
    }
}

# ['AppId', 'AppName', 'Services', 'Sensors', 'Users', 'Version']

db = client["userDB"]
collection = db.create_collection("TrafficCollection", **schema)
collection.insert_one(
    {
        "ApiKey": "qwr3r3fw3f23gfg",
        "Api": "wqeqw.com/function",
        "InputParams": ["abd", 123, 123.3254],
        "Status": 200,
    }
)
