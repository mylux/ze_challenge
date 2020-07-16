import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict

import boto3

import CourierSchema
from Authenticator import Authenticator
from BasicFlow import BasicFlow
from Hasher import Hasher
from InexistentResource import InexistentResource
from MissingData import MissingData
from RequestDispatcher import RequestDispatcher
from RequestParser import RequestParser
from SchemaValidator import SchemaValidator


def main(event=None, context=None):

    c: CourierManagementSystem = CourierManagementSystem()
    routes: dict = {
        'POST': {
            '/couriers': c.enroll
        },
        'GET': {
            '/couriers/view': c.get_courier_data
        },
        'PUT': {
            '/couriers/login': c.login,
            '/couriers': c.set_courier_data
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


class CourierManagementSystem(BasicFlow):
    def __init__(self):
        self.__valid_fields_create: list = ['username', 'courierName', 'address', 'password', 'phone']
        self.__valid_fields_update: list = ['username', 'courierName', 'address', 'phone']

        self.__account_data_schema: dict = CourierSchema.schema

        self.__dynamo_client = boto3.resource('dynamodb', region_name='us-east-2')

        super(CourierManagementSystem, self).__init__(self.__dynamo_client.Table("couriers"), CourierSchema.schema)

    def enroll(self, request_data: dict, request_context: dict) -> bool:
        return self.enroll_entity(request_data, self.__valid_fields_create)

    def login(self, request_data: dict, request_context: dict) -> str:
        return self.authenticate_entity(request_data, 'username', 'password')

    def get_courier_data(self, request_data: dict, request_context: dict) -> dict:
        return self.get_data(request_context, self.__valid_fields_update)

    def set_courier_data(self, request_data: dict, request_context: dict) -> bool:
        return self.set_data(request_data, request_context, self.__valid_fields_update)
