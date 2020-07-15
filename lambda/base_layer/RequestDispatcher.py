import json
import re
import traceback
from DecimalEncoder import DecimalEncoder


class RequestDispatcher:
    def __init__(self, request_data: dict, routes: dict, responses: dict):
        self.__request_data: dict = request_data
        self.__routes: dict = routes
        self.__responses: dict = responses

    def dispatch(self) -> dict:
        route_destination = self.__routes.get(
            self.__request_data.get('httpMethod', {})
        ).get(
            re.sub("/$", "", self.__request_data.get('path'))
        )
        status_code: int = 200
        result: str = ''
        request_data: dict = {}

        try:
            request_data: dict = json.loads(
                self.__request_data['body'] if self.__request_data['body'] else '{}'
            )
        except:
            status_code = 400
            result = "Malformed Request Data"

        try:
            if not result:
                result = route_destination(
                    request_data,
                    self.__request_data['requestContext']
                )
        except Exception as e:
            status_code = self.__responses.get(type(e), 500)

            if status_code == 500:
                traceback.print_exc()
            else:
                result = str(e)
        finally:
            body = json.dumps({
                'result': result
            }, cls=DecimalEncoder)
            return {'body': body, 'status_code': status_code}
