userCollectionSchema = {
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


ActiveNodeScema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['VMid', 'IP', 'Port', 'CPU', 'Memory', 'OtherStats'],
        'properties': {
            'VMid': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'IP': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'Port': {
                'bsonType': 'int',
                'description': 'must be a int and is required'
            },
            'CPU': {
                'bsonType': 'int',
                'description': 'must be a int and is required'
            },
            'Memory': {
                'bsonType': 'int',
                'description': 'must be a int and is required'
            },
            'OtherStats': {
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
