class RequestParser:
    def __init__(self, request_data: dict):
        self.__request_data: dict = request_data

    def get_user_id(self) -> str:
        return self.__request_data['authorizer']['principalId'] \
            if 'authorizer' in self.__request_data and 'principalId' in self.__request_data['authorizer'] else ""
