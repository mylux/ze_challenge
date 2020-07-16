import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr, Key
from moto import mock_dynamodb2
import pytest
import os
import orders_main

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
                    'AttributeName': 'shop_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'courier_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            TableName='orders',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'idx_user_id',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                },
                {
                    'IndexName': 'idx_courier_id',
                    'KeySchema': [
                        {
                            'AttributeName': 'courier_id',
                            'KeyType': 'HASH'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                },
                {
                    'IndexName': 'idx_shop_id',
                    'KeySchema': [
                        {
                            'AttributeName': 'shop_id',
                            'KeyType': 'HASH'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 3,
                        'WriteCapacityUnits': 3
                    }
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
        )
        resource = boto3.resource('dynamodb', region_name='us-east-2')
        table = resource.Table('orders')
        yield table


class TestOrders:
    def place_mock_order(self, database):
        payload_place = '''
    {
        "shop_id": "fake-shop-id",
        "user_id": "fake-user-id",
        "items": [
            {
                "item": "Coca-cola 2l",
                "price": 10.5
            },
            {
                "item": "Budweiser 350ml",
                "price": 5.5
            }
        ]
    }
'''
        x = orders_main.main(
            generate_event("/orders", "Users", "fake-user-id", "POST", payload_place),
            {}
        )

        return database.scan(
            TableName='orders',
            FilterExpression=Attr('user_id').eq("fake-user-id"),
            Limit=1
        ).get('Items', {})

    def test_place(self, database):
        orders = self.place_mock_order(database)
        assert len(orders) > 0
        order = orders[0]
        assert order['shop_id'] == 'fake-shop-id'
        assert order['user_id'] == "fake-user-id"
        assert order['items'][0]["item"] == "Coca-cola 2l"
        assert order['items'][0]["price"] == Decimal("10.5")
        assert order['items'][1]["item"] == "Budweiser 350ml"
        assert order['items'][1]["price"] == Decimal("5.5")

    def test_update(self, database):
        order = self.place_mock_order(database)[0]
        payload_update = '''
         {
            "id": "%s",
            "orderStatus": "InTransit",
            "courier_id": "475eb2ac-231b-4c60-b752-b404e89181ad"
        }
        ''' % order['id']

        response = orders_main.main(
            generate_event("/orders", "Shops", "fake-shop-id", "PUT", payload_update),
            {}
        )

        stored_order = database.get_item(Key={'id': order['id']})['Item']

        response_body = json.loads(response['body'])
        assert response_body.get("result")
        assert response['statusCode'] == 200
        assert order['orderStatus'] == "Placed"
        assert stored_order['orderStatus'] == "InTransit"
        assert stored_order['courier_id'] == "475eb2ac-231b-4c60-b752-b404e89181ad"
        assert stored_order["shop_id"] == order["shop_id"]
        assert stored_order["user_id"] == order["user_id"]
        assert stored_order["id"] == order["id"]
        assert stored_order["items"] == order["items"]

    def test_list_user_id(self, database):
        order = self.place_mock_order(database)[0]
        order_id = order.get("id")
        response = orders_main.main(
            generate_event("/orders", "Users", "fake-user-id", "GET", None),
            {}
        )
        response_body = json.loads(response['body'])
        returned_orders = response_body.get("result")

        assert len(returned_orders) == 1

        returned_order = returned_orders[0]

        assert returned_order['id'] == order_id
        assert returned_order['items'][0]["item"] == "Coca-cola 2l"
        assert returned_order['items'][0]["price"] == Decimal("10.5")
        assert returned_order['items'][1]["item"] == "Budweiser 350ml"
        assert returned_order['items'][1]["price"] == Decimal("5.5")
        assert response['statusCode'] == 200

    def test_list_shop_id(self, database):
        order = self.place_mock_order(database)[0]
        order_id = order.get("id")
        response = orders_main.main(
            generate_event("/orders", "Shops", "fake-shop-id", "GET", None),
            {}
        )
        response_body = json.loads(response['body'])
        returned_orders = response_body.get("result")

        assert len(returned_orders) == 1

        returned_order = returned_orders[0]

        assert returned_order['id'] == order_id
        assert returned_order['items'][0]["item"] == "Coca-cola 2l"
        assert returned_order['items'][0]["price"] == Decimal("10.5")
        assert returned_order['items'][1]["item"] == "Budweiser 350ml"
        assert returned_order['items'][1]["price"] == Decimal("5.5")
        assert response['statusCode'] == 200

    def test_amend(self, database):
        order = self.place_mock_order(database)[0]
        order_id = order.get("id")
        payload_amend = '''
        {
            "id": "%s",
            "items": [
                {
                    "item": "Sprite 2l",
                    "price": 8.0
                },
                {
                    "item": "Heineken 350ml",
                    "price": 5.6
                }
            ]
        }
        ''' % order_id

        response = orders_main.main(
            generate_event("/orders/amend", "Shops", "fake-shop-id", "PUT", payload_amend),
            {}
        )
        response_body = json.loads(response['body'])

        stored_order = database.get_item(Key={'id': order_id})['Item']

        assert response_body.get("result")
        assert response['statusCode'] == 200
        assert stored_order["orderStatus"] == order["orderStatus"]
        assert stored_order["shop_id"] == order["shop_id"]
        assert stored_order["user_id"] == order["user_id"]
        assert stored_order["id"] == order["id"]
        assert stored_order["items"][0]["item"] == "Sprite 2l"
        assert stored_order["items"][1]["item"] == "Heineken 350ml"
        assert stored_order["items"][0]["price"] == Decimal("8.0")
        assert stored_order["items"][1]["price"] == Decimal("5.6")
        assert order['items'][0]["item"] == "Coca-cola 2l"
        assert order['items'][0]["price"] == Decimal("10.5")
        assert order['items'][1]["item"] == "Budweiser 350ml"
        assert order['items'][1]["price"] == Decimal("5.5")
