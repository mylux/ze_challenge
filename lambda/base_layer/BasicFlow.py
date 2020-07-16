import uuid
from datetime import datetime

from Authenticator import Authenticator
from Hasher import Hasher
from InexistentResource import InexistentResource
from MissingData import MissingData

from RequestParser import RequestParser
from SchemaValidator import SchemaValidator
from inflector import Inflector


class BasicFlow:
    def __init__(self, table, schema: dict):
        self._table = table
        self._schema = schema
        self.__realm = self._table.name.capitalize()
        self.__entity_name: str = Inflector().singularize(self.__realm)

    def enroll_entity(self, request_data: dict, valid_fields: list, constants_to_add: dict = None):
        processed_data: dict = self._generate_data(request_data, valid_fields)
        self.__hash_password(processed_data)
        processed_data["id"] = str(uuid.uuid4())
        processed_data["created_at"] = int(datetime.now().timestamp())

        if constants_to_add:
            for c in constants_to_add:
                processed_data[c] = constants_to_add[c]

        self._table.put_item(Item=processed_data)
        return True

    def authenticate_entity(self, request_data: dict, username_field: str, password_field: str) -> str:
        username: str = request_data.get(username_field)
        password: str = request_data.get(password_field)
        access_token: str = Authenticator.login(self._table, {username_field: username}, password)

        if not access_token:
            raise InexistentResource("%s with these credentials does not exist" % self.__entity_name)
        return access_token

    def get_data(self, request_context: dict, valid_fields: list) -> dict:
        entity_id: str = self._require_session_id(request_context)
        entity: dict = self._table.get_item(
            Key={'id': entity_id},
            ProjectionExpression=','.join(valid_fields)
        ).get('Item')

        if not entity_id:
            raise InexistentResource("%s with id %s not found" % self.__entity_name, entity_id)
        return entity

    def set_data(self, request_data: dict, request_context, valid_fields: list):
        entity_id: str = self._require_session_id(request_context)
        entity_data: dict = self._generate_data(request_data, valid_fields)
        entity: dict = self._table.get_item(Key={'id': entity_id})['Item']

        entity.update(entity_data)

        self._table.put_item(Item=entity)
        return True

    def set_associated_data(
            self, associated_realm: str, request_data: dict, request_context: dict, valid_fields: list
    ) -> bool:
        associated_entity_id: str = self._require_session_id(request_context, associated_realm)
        associated_entity_name: str = Inflector().singularize(associated_realm).lower()

        entity_id: str = self.__require_entity_id_request(request_data)

        entity_data: dict = self._generate_data(request_data, valid_fields)
        entity: dict = self._table.get_item(Key={'id': entity_id})['Item']

        associated_id_field: str = "%s_id" % associated_entity_name
        stored_associated_entity_id: str = entity.get(associated_id_field)

        if associated_entity_id != stored_associated_entity_id:
            raise InexistentResource(
                'Not found an %s that belongs to this %s' % (self.__entity_name, associated_entity_name)
            )
        entity.update(entity_data)
        self._table.put_item(Item=entity)
        return True

    def __hash_password(self, account_data: dict):
        if 'password' in account_data:
            account_data['password'] = Hasher.hash_password(account_data['password'])

    def _generate_data(self, request_data: dict, valid_fields: list) -> dict:
        self._validate(request_data, valid_fields)
        values: list = [request_data[f] for f in valid_fields]
        processed_data: dict = dict(zip(valid_fields, values))
        return processed_data

    def _validate(self, request_data: dict, valid_fields: list):
        if not all([f in request_data for f in valid_fields]):
            raise MissingData('Missing fields in request data')

        try:
            SchemaValidator.validate(request_data, self._schema)
        except:
            raise MissingData("One or more fields have a mistake")

    def _require_session_id(self, request_context, realm=None) -> str:
        session_id: str = self._get_session_id(request_context, realm)
        if not session_id:
            entity_name: str = Inflector().singularize(realm)
            raise InexistentResource("%s with provided authentication token does not exist" % entity_name)
        return session_id

    def _get_session_id(self, request_context, realm=None) -> str:
        realm: str = realm if realm else self.__realm
        return RequestParser(request_context).get_user_id(realm)

    def __require_entity_id_request(self, request_data: dict):
        entity_id: str = request_data.get('id')
        if not entity_id:
            raise InexistentResource("%s does not exist" % self.__entity_name)
        return entity_id
