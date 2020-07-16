import boto3
import jwt
import traceback
import re


def main(event=None, context=None):
    effect: str = "Allow"
    alg: str = 'HS256'

    ssm_client = boto3.client('ssm', region_name="us-east-2")

    secret: str = ssm_client.get_parameter(
        Name='jws_key_parameter_name',
        WithDecryption=True
    )['Parameter']['Value']

    user_id: str = ""
    realm: str = ""
    authorization_matrix: dict = {
        'Users': [
            'users/login.PUT',
            'users/view.GET',
            'users.PUT',
            'users.POST',
            'shops.GET',
            'orders.POST',
            'orders.GET',
            'orders/view.GET'
        ],
        'Shops': [
            'shops.POST',
            'shops/view.GET',
            'shops/login.PUT',
            'shops.PUT',
            'orders.GET',
            'orders/view.GET',
            'orders.PUT',
            'orders/amend.PUT'
        ],
        'Couriers': [
            'couriers.POST',
            'couriers/login.PUT',
            'couriers/view.GET',
            'couriers.PUT',
            'orders.GET',
            'orders/view.GET'
        ]
    }

    try:
        path: str = re.sub(
            "/$",
            "",
            '/'.join(event['methodArn'].split('/')[3:])
        )

        method: str = event['methodArn'].split('/')[2]

        token: dict = jwt.decode(event['authorizationToken'], secret, algorithms=[alg])
        realm: str = list(token.keys())[0].split('.')[0] if len(token) > 0 else ''
        user_id = list(token.values())[0] if len(token) > 0 else ''

        authorization: bool = "%s.%s" % (path, method) in authorization_matrix.get(realm, [])
        effect = "Allow" if len(user_id) > 0 and authorization else "Deny"
    except jwt.InvalidSignatureError:
        effect = "Deny"
    except Exception as e:
        traceback.print_exc()
        effect = "Deny"

    policy = {
        "principalId": "%s/%s" % (realm, user_id),
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": event['methodArn']
                }
            ]
        }

    }

    return policy
