schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "default": {},
    "required": [
    ],
    "properties": {
        "shopName": {
            "type": "string"
        },
        "menu": {
            "type": "array",
            "default": [],
            "items": {
                "type": "object",
                "required": [
                    "item",
                    "price"
                ],
                "properties": {
                    "itemName": {
                        "type": "string"
                    },
                    "price": {
                        "type": "number"
                    }
                }
            }
        },
        "id": {
            "type": "string"
        },
        "username": {
            "type": "string"
        },
        "password": {
            "type": "string"
        },
        "address": {
            "type": "string"
        },
        "shopStatus": {
            "type": "string",
            "enum": ["Open", "open", "closed", "Closed"]
        }
    },
    "additionalProperties": False
}