schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "default": {},
    "required": [
    ],
    "properties": {
        "courierName": {
            "type": "string"
        },
        "address": {
            "type": "string"
        },
        "username": {
            "type": "string"
        },
        "password": {
            "type": "string"
        },
        "phone": {
            "type": "string",
            "pattern": "[0-9\\+]{9,}"
        }
    },
    "additionalProperties": False
}