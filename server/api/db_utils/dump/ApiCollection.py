import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"
)

schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "title": "Student Object Validation",
            "required": ["ApiKey", "developerId"],
            "properties": {
                "ApiKey": {"bsonType": "string"},
                "developerId": {"bsonType": "string"},
            },
        }
    }
}


db = client["userDB"]
collection = db.create_collection("ApiCollection", **schema)
collection.insert_one({"ApiKey": "qwr3r3fw3f23gfg", "developerId": "1273r82fyug"})
