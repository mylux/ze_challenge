from boto3.dynamodb.conditions import Attr, Key
import jwt
from Hasher import Hasher


class Authenticator:

    @staticmethod
    def login(table, username: dict, password: str) -> str:
        alg = 'HS256'
        secret = "o859758tw954tv97t5w9874987t5yw897tn9284gtv529t654btqn348cmr0348ruhq4yvt9t4rgq08nxr8qgfq"
        username_field_name: str = list(username.keys())[0]
        realm: str = table.name.capitalize()

        users: list = table.query(
            IndexName="idx_%s" % username_field_name,
            KeyConditionExpression=Key(username_field_name).eq(username[username_field_name])
        )['Items']
        user_id: str = users[0]['id'] if len(users) > 0 and 'id' in users[0] else {}

        user: dict = table.get_item(
            Key={'id': user_id}
        )['Item']

        if 'password' in user:
            return jwt.encode({"%s.id" % realm: user['id']}, secret, algorithm=alg).decode('utf-8') \
                if Hasher.verify_password(user['password'], password) else ""
