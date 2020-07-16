import json

import boto3
from boto3.dynamodb.conditions import Attr, Key
from moto import mock_dynamodb2
import pytest
import os
import shops_main

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


def generate_event(path, realm, shop_id, method, payload):
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
                "principalId": "%s/%s" % (realm, shop_id),
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
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                }
            ],
            TableName='shops',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'idx_username',
                    'KeySchema': [
                        {
                            'AttributeName': 'username',
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
        table = resource.Table('shops')
        yield table


class TestShops:
    def enroll_mock_shop(self, database):
        payload_enroll = '''
    {
        "username": "cornershop",
        "password":"12345678",
        "shopName": "Corner Shop",
        "shopStatus": "Open",
        "address": "Rua das Oiticicas 2018 lj 0601",
        "menu":[{"item": "Coca-Cola 2l", "price": 10.5}]
    }
'''
        shops_main.main(
            generate_event("/shops", "Shops", "", "POST", payload_enroll),
            {}
        )
        return database.scan(
            TableName='shops',
            FilterExpression=Attr('username').eq("cornershop"),
            Limit=1
        ).get('Items', {})

    def test_enroll(self, database):
        shops = self.enroll_mock_shop(database)
        assert len(shops) > 0
        shop = shops[0]
        assert shop['username'] == 'cornershop'
        assert shop['shopName'] == 'Corner Shop'
        assert shop['shopStatus'] == 'Open'
        assert shop['address'] == "Rua das Oiticicas 2018 lj 0601"
        assert shop['password'] != "12345678"

    def test_login(self, database):
        payload_login = '''{"username": "cornershop", "password": "12345678"}'''
        stored_shop = self.enroll_mock_shop(database)[0]

        response = shops_main.main(
            generate_event("/shops/login", "Shops", "", "PUT", payload_login),
            {}
        )
        response_body = json.loads(response['body'])
        assert len(response_body.get("result")) > 0 and ' ' not in response_body.get("result")
        assert response['statusCode'] == 200

    def test_get_data(self, database):
        shops = self.enroll_mock_shop(database)
        shop_id = shops[0].get("id")
        response = shops_main.main(
            generate_event("/shops/view", "Shops", shop_id, "GET", None),
            {}
        )
        response_body = json.loads(response['body'])
        returned_user = response_body.get("result")
        assert len(returned_user) > 0 and returned_user['username'] == 'cornershop'
        assert response['statusCode'] == 200

    def test_set_data(self, database):
        shops = self.enroll_mock_shop(database)
        shop_id = shops[0].get("id")
        payload_set_data = '''
        {
            "menu": [
                {
                    "item": "Coca-Cola 2l",
                    "price": 10.5
                },
                {
                    "item": "Budweiser 350ml",
                    "price": 5.2
                }
            ],
            "username": "cornershop",
            "address": "Rua das Oiticicas 2018 lj 0601",
            "shopName": "Corner Shop 2",
            "shopStatus": "Open"
        }
        '''

        response = shops_main.main(
            generate_event("/shops", "Shops", shop_id, "PUT", payload_set_data),
            {}
        )
        response_body = json.loads(response['body'])

        stored_shop = database.get_item(Key={'id': shop_id})['Item']

        assert shops[0]['shopName'] == "Corner Shop"
        assert response_body['result'] and isinstance(response_body['result'], bool)
        assert response['statusCode'] == 200
        assert stored_shop['username'] == 'cornershop'
        assert stored_shop['shopName'] == 'Corner Shop 2'
        assert stored_shop["shopStatus"] == "Open"
        assert stored_shop['id'] == shop_id
