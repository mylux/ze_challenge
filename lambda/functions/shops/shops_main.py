from decimal import Decimal

import boto3

import ShopSchema
from BasicFlow import BasicFlow
from InexistentResource import InexistentResource
from MissingData import MissingData
from RequestDispatcher import RequestDispatcher


def main(event=None, context=None):

    s: ShopManagementSystem = ShopManagementSystem()
    routes: dict = {
        'POST': {
            '/shops': s.enroll
        },
        'GET': {
            '/shops/view': s.get_shop_data
        },
        'PUT': {
            '/shops/login': s.login,
            '/shops': s.set_shop_data
        }
    }

    responses: dict = {
        InexistentResource: 404,
        MissingData: 400
    }

    r: RequestDispatcher = RequestDispatcher(event, routes, responses)

    response: dict = r.dispatch()

    return {
        "isBase64Encoded": False,
        "statusCode": response['status_code'],
        "headers": {},
        "multiValueHeaders": {},
        "body": response['body']
    }


class ShopManagementSystem(BasicFlow):
    def __init__(self):
        self.__valid_fields_create: list = ['username', 'shopName', 'address', 'password', 'shopStatus', 'menu']
        self.__valid_fields_update: list = ['username', 'shopName', 'address', 'shopStatus', 'menu']

        self.__dynamo_client = boto3.resource('dynamodb', region_name='us-east-2')
        super(ShopManagementSystem, self).__init__(self.__dynamo_client.Table("shops"), ShopSchema.schema)

    def enroll(self, account_data: dict, request_context: dict) -> bool:
        return self.enroll_entity(account_data, self.__valid_fields_create)

    def login(self, shop_data: dict, request_context: dict) -> str:
        return self.authenticate_entity(shop_data, 'username', 'password')

    def get_shop_data(self, account_data: dict, request_context: dict) -> dict:
        return self.get_data(request_context, self.__valid_fields_update)

    def set_shop_data(self, account_data: dict, request_context: dict) -> bool:
        return self.set_data(account_data, request_context, self.__valid_fields_update)
