class RequestParser:
    def __init__(self, request_data: dict):
        self.__request_data: dict = request_data

    def get_user_id(self, realm: str = "Users") -> str:
        user_id: str = ""
        session_user: str = self.__request_data.get("authorizer", {}).get("principalId", "")
        if session_user:
            session_realm, session_user_id = session_user.split("/")
            user_id: str = session_user_id if session_realm == realm else ""
        return user_id
