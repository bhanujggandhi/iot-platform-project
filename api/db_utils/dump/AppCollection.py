import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
)

schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "title": "Student Object Validation",
            "required": ["AppId", "AppName", "Services", "Sensors", "Users", "Version"],
            "properties": {
                "AppId": {"bsonType": "string"},
                "AppName": {"bsonType": "string"},
                "Services": {"bsonType": "array", "items": {"bsonType": "string"}},
                "Sensors": {"bsonType": "array", "items": {"bsonType": "string"}},
                "Users": {"bsonType": "array", "items": {"bsonType": "string"}},
                "Version": {"bsonType": "double"},
            },
        }
    }
}

# ['AppId', 'AppName', 'Services', 'Sensors', 'Users', 'Version']

db = client["userDB"]
collection = db.create_collection("AppCollection", **schema)
