import json

import boto3
from boto3.dynamodb.conditions import Attr, Key
from moto import mock_dynamodb2
import pytest
import os
import users_main

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


def generate_event(path, realm, user_id, method, payload):
    return {
        "resource": path,
        "path": path,
        "httpMethod": method,
        "headers":{
            "Accept": "* /*",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "queryStringParameters": "None",
        "multiValueQueryStringParameters": "None",
        "pathParameters":" None",
        "stageVariables": "None",
        "requestContext": {
            "resourceId": "u0b9f9",
            "authorizer": {
                "principalId": "%s/%s" % (realm, user_id),
                "integrationLatency": 236
            },
            "resourcePath": path,
            "httpMethod": method,
            "path": "/production%s" % path,
            "accountId": "070615495918",
        },
        "body": payload,
        "isBase64Encoded": False
    }


@pytest.fixture()
def database():
    with mock_dynamodb2():
        client = boto3.client('dynamodb', region_name='us-east-2')
        client.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'msisdn',
                    'AttributeType': 'S'
                }
            ],
            TableName='users',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'idx_msisdn',
                    'KeySchema': [
                        {
                            'AttributeName': 'msisdn',
                            'KeyType': 'HASH'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'KEYS_ONLY',
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                },
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
        )
        resource = boto3.resource('dynamodb', region_name='us-east-2')
        table = resource.Table('users')
        yield table


class TestUsers:
    def enroll_mock_user(self, database):
        payload_enroll = '''
    {"msisdn": "5511987654322", "password":"1234567", "first_name": "John", "surnames": "Doe", "birth_date": 315532800}
'''
        users_main.main(
            generate_event("/users", "Users", "", "POST", payload_enroll),
            {}
        )
        return database.scan(
            TableName='users',
            FilterExpression=Attr('msisdn').eq("5511987654322"),
            Limit=1
        ).get('Items', {})

    def test_enroll(self, database):
        users = self.enroll_mock_user(database)
        assert len(users) > 0
        user = users[0]
        assert user['msisdn'] == '5511987654322'
        assert user['first_name'] == 'John'
        assert user['password'] != "1234567"

    def test_login(self, database):
        payload_login = '''{"msisdn": "5511987654322", "password": "1234567"}'''
        self.enroll_mock_user(database)

        response = users_main.main(
            generate_event("/users/login", "Users", "", "PUT", payload_login),
            {}
        )
        response_body = json.loads(response['body'])
        assert len(response_body.get("result")) > 0 and ' ' not in response_body.get("result")
        assert response['statusCode'] == 200

    def test_get_data(self, database):
        users = self.enroll_mock_user(database)
        user_id = users[0].get("id")
        response = users_main.main(
            generate_event("/users/view", "Users", user_id, "GET", None),
            {}
        )
        response_body = json.loads(response['body'])
        returned_user = response_body.get("result")
        assert len(returned_user) > 0 and returned_user['msisdn'] == '5511987654322'
        assert response['statusCode'] == 200

    def test_set_data(self, database):
        users = self.enroll_mock_user(database)
        user_id = users[0].get("id")
        payload_set_data = '''
{"msisdn": "5511987654321", "first_name": "John 2", "surnames": "Doe 2", "birth_date": 315532800}
        '''

        response = users_main.main(
            generate_event("/users", "Users", user_id, "PUT", payload_set_data),
            {}
        )
        response_body = json.loads(response['body'])

        stored_user = database.get_item(Key={'id': user_id})['Item']

        assert response_body['result'] and isinstance(response_body['result'], bool)
        assert response['statusCode'] == 200
        assert stored_user['msisdn'] == '5511987654321'
        assert stored_user['first_name'] == 'John 2'
        assert stored_user['id'] == user_id
