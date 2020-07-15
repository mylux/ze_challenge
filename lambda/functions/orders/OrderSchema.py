schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "default": {},
    "required": [
    ],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string"
                    },
                    "price": {
                        "type": "number"
                    }
                },
                "additionalProperties": False
            }
        },
        "shop_id": {
            "type": "string"
        },
        "user_id": {
            "type": "string"
        },
        "courier_id": {
            "type": "string"
        },
        "orderStatus": {
            "type": "string",
            "enum": [
                "Canceled",
                "Delivered",
                "InTransit",
                "Confirmed",
                "Placed"
            ]
        },
        "id": {
            "type": "string"
        }
    },
    "additionalProperties": False
}
