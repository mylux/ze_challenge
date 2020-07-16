import json

import boto3
from boto3.dynamodb.conditions import Attr, Key
from moto import mock_dynamodb2
import pytest
import os
import couriers_main

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
            TableName='couriers',
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
        table = resource.Table('couriers')
        yield table


class TestCouriers:
    def enroll_mock_courier(self, database):
        payload_enroll = '''
    {
        "username": "loggi",
        "password": "123456789",
        "address": "Rua do Guaiaó 2017, Cj 0112",
        "phone": "551133456789",
        "courierName": "Loggi Delivery"
    }
'''
        couriers_main.main(
            generate_event("/couriers", "Couriers", "", "POST", payload_enroll),
            {}
        )
        return database.scan(
            TableName='couriers',
            FilterExpression=Attr('username').eq("loggi"),
            Limit=1
        ).get('Items', {})

    def test_enroll(self, database):
        couriers = self.enroll_mock_courier(database)
        assert len(couriers) > 0
        courier = couriers[0]
        assert courier['username'] == 'loggi'
        assert courier['courierName'] == 'Loggi Delivery'
        assert courier['address'] == "Rua do Guaiaó 2017, Cj 0112"
        assert courier['password'] != "123456789"

    def test_login(self, database):
        payload_login = '''{"username": "loggi", "password": "123456789"}'''
        stored_courier = self.enroll_mock_courier(database)[0]

        response = couriers_main.main(
            generate_event("/couriers/login", "Couriers", "", "PUT", payload_login),
            {}
        )
        response_body = json.loads(response['body'])
        assert len(response_body.get("result")) > 0 and ' ' not in response_body.get("result")
        assert response['statusCode'] == 200

    def test_get_data(self, database):
        couriers = self.enroll_mock_courier(database)
        courier_id = couriers[0].get("id")
        response = couriers_main.main(
            generate_event("/couriers/view", "Couriers", courier_id, "GET", None),
            {}
        )
        response_body = json.loads(response['body'])
        returned_user = response_body.get("result")
        assert len(returned_user) > 0 and returned_user['username'] == 'loggi'
        assert response['statusCode'] == 200

    def test_set_data(self, database):
        couriers = self.enroll_mock_courier(database)
        courier_id = couriers[0].get("id")
        payload_set_data = '''
        {
    "username": "loggi",
    "address": "Rua do Guaiaó 2017, Cj 0112",
    "courierName": "The Loggi Delivery",
    "phone": "551133456789"
}
        '''

        response = couriers_main.main(
            generate_event("/couriers", "Couriers", courier_id, "PUT", payload_set_data),
            {}
        )
        response_body = json.loads(response['body'])

        stored_courier = database.get_item(Key={'id': courier_id})['Item']

        assert couriers[0]['courierName'] == "Loggi Delivery"
        assert response_body['result'] and isinstance(response_body['result'], bool)
        assert response['statusCode'] == 200
        assert stored_courier['username'] == 'loggi'
        assert stored_courier['courierName'] == 'The Loggi Delivery'
        assert stored_courier["phone"] == "551133456789"
        assert stored_courier['id'] == courier_id
