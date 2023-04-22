import pymongo
from bson.json_util import dumps

from decouple import config


class DataBase:
    def __init__(self):
        self.client = None
        self.db = None
        self.data = None
        self.collection = None

    def connect(self):
        mongoKey = config("mongoKey")
        self.client = pymongo.MongoClient(mongoKey)

    def create_db(self, db_name: str):
        self.db = self.client[db_name]

    def use_collection(self, collection_name: str):
        self.collection = self.db[collection_name]

    def model(self, data):
        self.data = data

    def add(self):
        self.collection.insert_one(self.data)
        return {"message": "Document added successfully"}

    def update(self, field, old_str, new_str):
        old_values = {f"{field}": old_str}
        new_values = {"$set": {f"{field}": new_str}}
        self.collection.update_one(old_values, new_values)
        return {"message": "Document updated successfully"}

    def delete(self, field, value):
        self.collection.delete_one({f"{field}": value})
        return {"message": "Document deleted successfully"}

    def read(self):
        return dumps(list(self.collection.find()))

    def join(self, fromCollection, localField, foreignField):
        result = self.collection.aggregate(
            [
                {
                    "$lookup": {
                        "from": f"{fromCollection}",
                        "localField": f"{localField}",
                        "foreignField": f"{foreignField}",
                        "as": "results",
                    }
                }
            ]
        )
        return dumps(list(result))
