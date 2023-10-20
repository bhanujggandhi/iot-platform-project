## Template for MongoDB Schema Documentation

### Schema

1. from decoupler import config
2. from pymongo import MongoClient
3. mongokey = config('mongoKey')
4. client = MongoClient(mongokey)
5. db = client['YOUR DB NAME']
6. collection = db.YOUR_COLLECTION_NAME
7. collection.insert_one({
   FOLLOW SCHEMA TO INSERT
   })
