from pymongo import MongoClient
import pymongo
from decouple import config

ActiveNodeSchema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["VMid", "IP", "Port", "CPU", "Memory", "OtherStats"],
        "properties": {
            "VMid": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "IP": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "Port": {"bsonType": "int", "description": "must be a int and is required"},
            "CPU": {"bsonType": "int", "description": "must be a int and is required"},
            "Memory": {
                "bsonType": "int",
                "description": "must be a int and is required",
            },
            "OtherStats": {
                "bsonType": "array",
                "description": "must be an array and is required",
                "items": {
                    "bsonType": "string",
                    "description": "must be a string if the field is present",
                },
            },
        },
    }
}

# (DB:userDB, collection:userCollection )
userCollectionSchema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "role", "email", "password"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "role": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
        },
    }
}

# (DB:userDB , collection:ApiCollection)
ApiCollectionSchema = {
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

# (DB:userDB , collection:AppCollection )
AppCollectionSchema = {
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
# (DB:userDB , collection:TrafficCollection )
TrafficCollectionSchema = {
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


# (DB:platform , collection:Module_Status)
Module_StatusSchema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "title": "Student Object Validation",
            "required": ["module_name", "status", "last_updated"],
            "properties": {
                "module_name": {"bsonType": "string"},
                "status": {"bsonType": "string"},
                "last_updated": {"bsonType": "date"},
            },
        }
    }
}
