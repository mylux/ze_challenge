schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "default": {},
    "required": [
    ],
    "properties": {
        "msisdn": {
            "type": "string",
            "pattern": "[0-9\\+]{9,}"
        },
        "id": {
            "type": "string"
        },
        "first_name": {
            "type": "string"
        },
        "password": {
            "type": "string"
        },
        "surnames": {
            "type": "string"
        },
        "birth_date": {
            "type": "integer"
        }
    },
    "additionalProperties": False
}