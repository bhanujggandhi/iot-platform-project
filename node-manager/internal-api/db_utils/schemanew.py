# (DB:ActiveNodeDB , collection:activeNodeCollection)
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
        "required": [
            "developerId",
            "developerName",
            "Role",
            "email",
            "password",
            "Appids",
        ],
        "properties": {
            "developerId": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "developerName": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "Role": {
                "enum": ["AppAdmin", "AppDeveloper", "PlatformAdmin"],
                "description": "can only be one of the enum values and is required",
            },
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "Appids": {
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

activeNodeCollectionSchema = {
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
