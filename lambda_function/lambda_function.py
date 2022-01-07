import sys
sys.path.append("/opt/third_party")

try:
    import paramiko
except ModuleNotFoundError as err:
    print(f"{err}")
    sys.exit()

import os
import pprint


def lambda_handler(event, context):
    print("version: ", 1)
    print(f"{os.environ.get('LICENSE')=}")
    print(f"{os.environ.get('RELEASE')=}")
    pprint.pprint(event)
    client = paramiko.SSHClient()
    pprint.pprint(client)

    return {
        'statusCode': 200,
        'body': "DONE"
    }
