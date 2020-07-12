import jwt
import traceback


def main(event=None, context=None):
    effect = "Allow"
    alg = 'HS256'
    secret = "o859758tw954tv97t5w9874987t5yw897tn9284gtv529t654btqn348cmr0348ruhq4yvt9t4rgq08nxr8qgfq"

    try:
        jwt.decode(event['authorizationToken'], secret, algorithms=[alg])
    except jwt.InvalidSignatureError:
        effect = "Deny"
    except Exception as e:
        traceback.print_exc()
        effect = "Deny"

    policy = {
        "principalId": "any_user",
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
