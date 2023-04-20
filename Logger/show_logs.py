"""
Show the logs captured into MongoDB collection
"""
import time
from pymongo import MongoClient

# mongoKey = config("mongoKey")
mongoKey = "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority"

# Get the list of logging entries in MongoDB collection
client = MongoClient(mongoKey)
db = client.LoggerDB
collection = db.loggingCollection

# find all data in DB
cursor = collection.find(sort=[("timestamp", 1)])

latest_timetimestamp = 0

# Sort the documents on the basis of their created time and display onto stdout
for document in cursor:
    if document["timestamp"] > latest_timetimestamp:
        latest_timetimestamp = document["timestamp"]

    string = f'{document["timestamp"]} | {document["level"]} ({document["module"]}): {document["msg"]}'
    print(string)

while True:
    try:
        # get the latest data entry in collection
        document = collection.find_one(sort=[("timestamp", -1)])
        if document["timestamp"] > latest_timetimestamp:
            latest_timetimestamp = document["timestamp"]
            string = f'{document["timestamp"]} | {document["level"]} ({document["module"]}): {document["msg"]}'
            print(string)
    except KeyboardInterrupt:
        break
