import boto3 as boto3
from boto3.dynamodb.conditions import Attr, Key
import uuid
from Hasher import Hasher
import jwt
import json
import re
import traceback
from datetime import datetime


def main(event=None, context=None):
    u: UserManagementSystem = UserManagementSystem()
    routes: dict = {
        'POST': {
            '/users': u.enroll
        },
        'GET': {
            '/users': u.get_account_data
        },
        'PUT': {
            '/users/login': u.login
        }
    }
    route_destination = routes.get(
        event.get('httpMethod', {})
    ).get(
        re.sub("/$", "", event.get('path'))
    )
    result: str = json.dumps({
        'result': route_destination(json.loads(event['body']))
    })

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "multiValueHeaders": {},
        "body": result
    }


class UserManagementSystem:
    def __init__(self):
        self.__valid_fields_create: list = ['msisdn', 'first_name', 'surnames', 'password']
        self.__valid_fields_update: list = ['first_name', 'surnames', 'birth_date', 'password']
        self.__dynamo_client = boto3.resource('dynamodb')
        self.__table = self.__dynamo_client.Table('users')

    def login(self, user_data: dict) -> str:
        msisdn: str = user_data.get("msisdn")
        password: str = user_data.get("password")
        effect = "Allow"
        alg = 'HS256'
        secret = "o859758tw954tv97t5w9874987t5yw897tn9284gtv529t654btqn348cmr0348ruhq4yvt9t4rgq08nxr8qgfq"

        users: list = self.__table.query(
            IndexName="user_msisdn",
            FilterExpression=Key("msisdn").eq(msisdn)
        )['Items']
        user: dict = users[0] if len(users) > 0 else {}
        if 'password' in user:
            return jwt.encode({"User.id": user['id']}, secret, algorithm=alg)\
                if Hasher.hash_password(password) == user['password'] else ""

    def get_account_data(self, account_data: dict) -> dict:
        pass

    def set_account_data(self, account_data: dict) -> bool:
        return self.enroll(account_data)

    def enroll(self, account_data: dict) -> bool:
        try:
            self.__hash_password(account_data)
            user_data: dict = self.__generate_user_data(account_data, self.__valid_fields_create)
            user_data["id"] = str(uuid.uuid4())
            user_data["created_at"] = int(datetime.now().timestamp())

            self.__table.put_item(
                Item=user_data,
                ConditionExpression=Attr("msisdn").not_exists()
            )
            return True
        except:
            traceback.print_exc()
            return False

    def __generate_user_data(self, account_data: dict, valid_fields: list) -> dict:
        if not all([f in account_data for f in valid_fields]):
            raise Exception('Missing fields in account data')

        values: list = [account_data[f] for f in valid_fields]
        user_data: dict = dict(zip(self.__valid_fields_create, values))
        return user_data

    def __hash_password(self, account_data: dict):
        if 'password' in account_data:
            account_data['password'] = Hasher.hash_password(account_data['password'])

