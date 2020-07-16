import boto3
from boto3.dynamodb.conditions import Key

import OrderSchema
from BasicFlow import BasicFlow
from InexistentResource import InexistentResource
from MissingData import MissingData
from RequestDispatcher import RequestDispatcher


def main(event=None, context=None):

    o: OrderManagementSystem = OrderManagementSystem()
    routes: dict = {
        'POST': {
            '/orders': o.place
        },
        'GET': {
            '/orders': o.list
        },
        'PUT': {
            '/orders/amend': o.amend,
            '/orders': o.update
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


class OrderManagementSystem(BasicFlow):
    def __init__(self):
        self.__valid_fields_create: list = ['user_id', 'shop_id', 'items']
        self.__valid_fields_update: list = ['courier_id', 'orderStatus', "id"]
        self.__valid_fields_amend: list = ['items', 'id']

        self.__dynamo_client = boto3.resource('dynamodb', region_name='us-east-2')
        self.__table = self.__dynamo_client.Table("orders")
        super(OrderManagementSystem, self).__init__(self.__dynamo_client.Table("orders"), OrderSchema.schema)

    def list(self, order_request_data: dict, request_context: dict) -> list:
        user_id: str = self._get_session_id(request_context, "Users")
        shop_id: str = self._get_session_id(request_context, "Shops")

        if not user_id and not shop_id:
            raise InexistentResource("No user or shop identified")

        search_field: dict = {"user_id": user_id} if user_id else {"shop_id": shop_id}

        search_field_name = list(search_field.keys())[0]

        return self.__table.query(
            IndexName="idx_%s" % list(search_field.keys())[0],
            KeyConditionExpression=Key(search_field_name).eq(search_field[search_field_name])
        ).get('Items', [])

    def place(self, order_request_data: dict, request_context: dict) -> bool:
        additional_data: dict = {
            'user_id': self._require_session_id(request_context, "Users"),
            'orderStatus': 'Placed'
        }

        return self.enroll_entity(order_request_data, self.__valid_fields_create, additional_data)

    def update(self, order_request_data: dict, request_context: dict):
        return self.set_associated_data("Shops", order_request_data, request_context, self.__valid_fields_update)

    def amend(self, order_request_data: dict, request_context: dict):
        return self.set_associated_data("Shops", order_request_data, request_context, self.__valid_fields_amend)
