import pymongo
import schema

client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority")

dbs = {
    "userDB": ["userCollection", "ApiCollection", "AppCollection", "TrafficCollection"],
    "ActiveNodeDB": ["activeNodeCollection"],
    "SensorDB": ["SensorData", "SensorMetadata"],
}

for db in dbs.keys():
    create_db = client[db]

    for collection in dbs[db]:
        if collection not in create_db.list_collection_names():
            var = collection + "Schema"
            collectionschema = getattr(schema, var)
            # print(**collectionschema)
            new_collection = create_db.create_collection(collection, collectionschema)
