import pymongo
# from decouple import config

# Set up a MongoDB client
# mongoKey = config('mongoKey')
client = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.ybcfbgy.mongodb.net/?retryWrites=true&w=majority")

# Define a list of databases and collections to create
dbs_and_collections = [
    {
        'db_name': 'UserDB',
        'collections': [
            {
                'name': 'UserCollection',
                'schema': {
                    'developerId': {'bsonType': 'string'},
                    'developerName': {'bsonType': 'string'},
                    'Role': {'enum': ['AppAdmin', 'AppDeveloper', 'PlatformAdmin']},
                    'email': {'bsonType': 'string', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'},
                    'password': {'bsonType': 'string'},
                    'ApiIds': {'bsonType': 'array', 'items': {'bsonType': 'string'}}
                }
            },
            {
                'name': 'AppCollection',
                'schema': {
                    'AppId': {'bsonType': 'string'},
                    'AppName': {'bsonType': 'string'},
                    'Services': {'bsonType': 'array', 'items': {'bsonType': 'string'}},
                    # SENSOR TYPE CAN BE ENUM
                    'Sensors': {'bsonType': 'array', 'items': {'bsonType': 'string'}},
                    'Users': {'bsonType': 'array', 'items': {'bsonType': 'string'}},
                    'Version': {'bsonType': 'double'}
                }
            },
            {
                'name': 'ApiCollection',
                'schema': {
                    'ApiKey': {'bsonType': 'string'},
                    'developerId': {'bsonType': 'string'}
                }
            },
            {
                'name': 'TrafficCollection',
                'schema': {
                    'ApiKey': {'bsonType': 'string'},
                    'Api': {'bsonType': 'string'},
                    'inputParmas': {'bsonType': 'array', 'items': {
                        'bsonType': 'oneOf',
                        'oneOf': [
                            {'bsonType': 'string'},
                            {'bsonType': 'int'},
                            {'bsonType': 'double'}
                        ]
                    }},
                }
            }
        ]
    }
    # {
    #     'db_name': 'mydatabase2',
    #     'collections': [
    #         {
    #             'name': 'my_collection3',
    #             'schema': {
    #                 'title': {'bsonType': 'string'},
    #                 'description': {'bsonType': 'string'},
    #                 'category': {'bsonType': 'string'}
    #             }
    #         },
    #         {
    #             'name': 'my_collection4',
    #             'schema': {
    #                 'name': {'bsonType': 'string'},
    #                 'age': {'bsonType': 'int'},
    #                 'email': {'bsonType': 'string', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}
    #             }
    #         }
    #     ]
    # }
]

# # Loop through the list of databases and collections
# for db_and_collections in dbs_and_collections:
#     # Check if the database already exists
#     if db_and_collections['db_name'] not in client.list_database_names():
#         # Create the database
#         db = client[db_and_collections['db_name']]

#         # Loop through the collections for this database
#         for collection_info in db_and_collections['collections']:
#             # Check if the collection already exists
#             if collection_info['name'] not in db.list_collection_names():
#                 # Create the collection with the specified schema
#                 collection = db.create_collection(
#                     collection_info['name'], **collection_info['schema'])

#                 # Print a message indicating the collection was created
#                 print(
#                     f"Created collection {collection_info['name']} in database {db_and_collections['db_name']}")
#             else:
#                 # Print a message indicating the collection already exists
#                 print(
#                     f"Collection {collection_info['name']} already exists in database {db_and_collections['db_name']}")
#     else:
#         # Print a message indicating the database already exists
#         print(f"Database {db_and_collections['db_name']} already exists")
# userDB = dbs_and_collections[0]['collections'][0]['name']
# schema = dbs_and_collections[0]['collections'][0]['schema']
# db = client['userDB']
# collection = db.UserCollection

# collection = db

# collection = db.create_collection(userDB, validator=schema)
uservalidator = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['developerId', 'developerName', 'Role', 'email', 'password', 'Appids'],
        'properties': {
            'developerId': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'developerName': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'Role': {
                'enum': ['AppAdmin', 'AppDeveloper', 'PlatformAdmin'],
                'description': 'can only be one of the enum values and is required'
            },
            'email': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'password': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'Appids': {
                'bsonType': 'array',
                'description': 'must be an array and is required',
                'items': {
                    'bsonType': 'string',
                    'description': 'must be a string if the field is present'
                }
            }
        }
    }

}
db = client['userDB']

# collection = db.create_collection("userCollection", validator=uservalidator)
# modify the validator for the userCollection collection
userCollection = db.userCollection
userCollection.drop()
userCollection = db.create_collection(
    "userCollection", validator=uservalidator)

# collection = db.userCollection
# collection = db.userDB
print("Insering One :")
userCollection.insert_one({
    "developerId": "1234",
    "developerName": "Vaibhav",
    "Role": "AppAdmin",
    'email': "vaibhav.work07@gmaik.com",
    'password': "123456",
    'Appids': ["12", "321"]


})

# collection.insert_one({
#     "developerId": 1234,
#     "developerName": "Vaibhav",
#     "Role": "AppAdmin",
#     'email': "vaibhav.work07@gmail.com",
#     "password": "123456",
#     "Appids": ["12", "321"]

# }
# )
