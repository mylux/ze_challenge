import boto3 as boto3

import UserSchema
from BasicFlow import BasicFlow
from InexistentResource import InexistentResource
from MissingData import MissingData
from RequestDispatcher import RequestDispatcher


def main(event=None, context=None):
    u: UserManagementSystem = UserManagementSystem()
    routes: dict = {
        'POST': {
            '/users': u.enroll
        },
        'GET': {
            '/users/view': u.get_account_data
        },
        'PUT': {
            '/users/login': u.login,
            '/users': u.set_account_data
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


class UserManagementSystem(BasicFlow):
    def __init__(self):
        self.__valid_fields_create: list = ['msisdn', 'first_name', 'surnames', 'password', 'birth_date']
        self.__valid_fields_update: list = ['msisdn', 'first_name', 'surnames', 'birth_date']
        self.__dynamo_client = boto3.resource('dynamodb', region_name = "us-east-2")
        super(UserManagementSystem, self).__init__(self.__dynamo_client.Table("users"), UserSchema.schema)

    def login(self, user_data: dict, request_context: dict) -> str:
        return self.authenticate_entity(user_data, 'msisdn', 'password')

    def get_account_data(self, account_data: dict, request_context: dict) -> dict:
        return self.get_data(request_context, self.__valid_fields_update)

    def set_account_data(self, account_data: dict, request_context: dict) -> bool:
        return self.set_data(account_data, request_context, self.__valid_fields_update)

    def enroll(self, request_data: dict, request_context: dict):
        return self.enroll_entity(request_data, self.__valid_fields_create)
