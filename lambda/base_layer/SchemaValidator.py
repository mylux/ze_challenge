import jsonschema


class SchemaValidator:
    @staticmethod
    def validate(instance: dict, schema: dict):
        jsonschema.validate(instance=instance, schema=schema)
