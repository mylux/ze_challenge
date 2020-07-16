schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "default": {},
    "required": [
    ],
    "properties": {
        "first_name": {
            "type": "string"
        },
        "birth_date": {
            "type": "integer"
        },
        "password": {
            "type": "string"
        },
        "surnames": {
            "type": "string"
        },
        "msisdn": {
            "type": "string",
            "pattern": "[0-9\\+]{9,}"
        }
    },
    "additionalProperties": False
}
