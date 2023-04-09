import pymongo

# Set up a MongoDB client
client = pymongo.MongoClient()

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
                    'Role': {'bsonType': 'string'},
                    'email': {'bsonType': 'string', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'},
                    'password': {}
                }
            },
            {
                'name': 'AppCollection',
                'schema': {
                    'name': {'bsonType': 'string'},
                    'age': {'bsonType': 'int'},
                    'gender': {'enum': ['male', 'female', 'other']}
                }
            },
            {
                'name': 'ApiCollection',
                'schema': {
                    'name': {'bsonType': 'string'},
                    'age': {'bsonType': 'int'},
                    'gender': {'enum': ['male', 'female', 'other']}
                }
            },
            {
                'name': 'TrafficCollection',
                'schema': {
                    'name': {'bsonType': 'string'},
                    'age': {'bsonType': 'int'},
                    'gender': {'enum': ['male', 'female', 'other']}
                }
            }
        ]
    },
    {
        'db_name': 'mydatabase2',
        'collections': [
            {
                'name': 'my_collection3',
                'schema': {
                    'title': {'bsonType': 'string'},
                    'description': {'bsonType': 'string'},
                    'category': {'bsonType': 'string'}
                }
            },
            {
                'name': 'my_collection4',
                'schema': {
                    'name': {'bsonType': 'string'},
                    'age': {'bsonType': 'int'},
                    'email': {'bsonType': 'string', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}
                }
            }
        ]
    }
]

# Loop through the list of databases and collections
for db_and_collections in dbs_and_collections:
    # Check if the database already exists
    if db_and_collections['db_name'] not in client.list_database_names():
        # Create the database
        db = client[db_and_collections['db_name']]

        # Loop through the collections for this database
        for collection_info in db_and_collections['collections']:
            # Check if the collection already exists
            if collection_info['name'] not in db.list_collection_names():
                # Create the collection with the specified schema
                collection = db.create_collection(
                    collection_info['name'], **collection_info['schema'])

                # Print a message indicating the collection was created
                print(
                    f"Created collection {collection_info['name']} in database {db_and_collections['db_name']}")
            else:
                # Print a message indicating the collection already exists
                print(
                    f"Collection {collection_info['name']} already exists in database {db_and_collections['db_name']}")
    else:
        # Print a message indicating the database already exists
        print(f"Database {db_and_collections['db_name']} already exists")
