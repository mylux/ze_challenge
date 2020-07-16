import boto3
from boto3.dynamodb.conditions import Attr, Key
import jwt
from Hasher import Hasher


class Authenticator:

    @staticmethod
    def login(table, username: dict, password: str) -> str:
        alg = 'HS256'
        ssm_client = boto3.client('ssm')

        secret: str = ssm_client.get_parameter(
            Name='jws_key_parameter_name',
            WithDecryption=True
        )['Parameter']['Value']

        username_field_name: str = list(username.keys())[0]
        realm: str = table.name.capitalize()

        users: list = table.query(
            IndexName="idx_%s" % username_field_name,
            KeyConditionExpression=Key(username_field_name).eq(username[username_field_name])
        ).get('Items', [])
        user_id: str = users[0]['id'] if len(users) > 0 and 'id' in users[0] else ''

        if not user_id:
            return ""

        user: dict = table.get_item(
            Key={'id': user_id}
        ).get('Item', {})

        return jwt.encode({"%s.id" % realm: user['id']}, secret, algorithm=alg).decode('utf-8') \
            if Hasher.verify_password(user.get('password', ''), password) else ""
