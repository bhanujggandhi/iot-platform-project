from decouple import config
from pymongo import MongoClient
mongokey = config('mongoKey')
client = MongoClient(mongokey)

db = client['userDB']
collection = db.AppCollection

for document in collection.find():
    print(document)

#fetching developer id

#fetching apps of that developer