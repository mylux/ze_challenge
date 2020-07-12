def main(event=None, context=None):
    x = str(event)
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "multiValueHeaders": {},
        "body": 'Couriers application\n %s' % x
    }
