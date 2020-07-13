import jwt
import traceback


def main(event=None, context=None):
    effect = "Allow"
    alg = 'HS256'
    secret = "o859758tw954tv97t5w9874987t5yw897tn9284gtv529t654btqn348cmr0348ruhq4yvt9t4rgq08nxr8qgfq"
    user_id = ""

    try:
        token: dict = jwt.decode(event['authorizationToken'], secret, algorithms=[alg])
        user_id = token['User.id'] if 'User.id' in token else ''
        effect = "Allow" if len(user_id) > 0 else "Deny"
    except jwt.InvalidSignatureError:
        effect = "Deny"
    except Exception as e:
        traceback.print_exc()
        effect = "Deny"

    policy = {
        "principalId": user_id,
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
