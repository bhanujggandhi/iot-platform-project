serCollectionSchema = {
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
