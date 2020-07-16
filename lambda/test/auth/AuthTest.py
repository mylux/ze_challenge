import json

import boto3
import jwt
from moto import mock_ssm
import pytest
import os
import auth_main

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


@pytest.fixture()
def parameter_store():
    with mock_ssm():
        client = boto3.client('ssm', region_name="us-east-2")
        yield client


def create_secret_key(client):
    client.put_parameter(
        Name='jws_key_parameter_name',
        Value='myfakesecretkey123..',
        Type='SecureString',
        Overwrite=True,
        Tier='Standard'
    )


def generate_token(ssm_client, realm):
    alg = 'HS256'
    secret: str = ssm_client.get_parameter(
        Name='jws_key_parameter_name',
        WithDecryption=True
    )['Parameter']['Value']
    return jwt.encode({"%s.id" % realm: "1234"}, secret, algorithm=alg).decode('utf-8')


def generate_event(method, path, authorization_token):
    return {
        "methodArn":  "arn:aws:execute-api:us-east-x:123456789012:myapiid/*/%s/%s" % (method, path),
        "authorizationToken": authorization_token
    }


class TestAuth:
    def test_auth_allow(self, parameter_store):
        create_secret_key(parameter_store)
        token = generate_token(parameter_store, "Users")
        event = generate_event("GET", "orders", token)

        result = auth_main.main(event, None)

        assert "principalId" in result
        assert result['principalId'] == "Users/1234"
        assert result['policyDocument']['Statement'][0]['Action'] == 'execute-api:Invoke'
        assert result['policyDocument']['Statement'][0]['Effect'] == 'Allow'

    def test_auth_forbidden_access(self, parameter_store):
        create_secret_key(parameter_store)
        token = generate_token(parameter_store, "Users")
        event = generate_event("GET", "shops/view", token)

        result = auth_main.main(event, None)

        assert "principalId" in result
        assert result['principalId'] == "Users/1234"
        assert result['policyDocument']['Statement'][0]['Action'] == 'execute-api:Invoke'
        assert result['policyDocument']['Statement'][0]['Effect'] == 'Deny'

    def test_auth_wrong_token_access(self, parameter_store):
        create_secret_key(parameter_store)
        token = "messeduptoken"
        event = generate_event("GET", "users/view", token)

        result = auth_main.main(event, None)

        assert "principalId" in result
        assert result['principalId'] == "/"
        assert result['policyDocument']['Statement'][0]['Action'] == 'execute-api:Invoke'
        assert result['policyDocument']['Statement'][0]['Effect'] == 'Deny'
