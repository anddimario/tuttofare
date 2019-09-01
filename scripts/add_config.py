import boto3
import uuid
import yaml
import sys
from datetime import datetime, time

def main():
    stream = open("./config.yaml", "r")
    config = yaml.load(stream, Loader=yaml.FullLoader)

    dynamodb = boto3.client(
        'dynamodb',
        aws_access_key_id=config["aws"]["ACCESS_KEY"],
        aws_secret_access_key=config["aws"]["SECRET_KEY"],
        region_name=config["aws"]["REGION"],
        endpoint_url=config["aws"]["DYNAMODB_ENDPOINT"], # use localstack: http://localhost:4569
    )

    Item={
        'id': {'S': str(uuid.uuid4())},
        'tuttofare_type': {'S': sys.argv[1]},
        'interval': {'S': sys.argv[2]},
    }

    if int(sys.argv[2]) > 0:
        Item["last_execution"] = {'S': str(datetime.now())}

    if sys.argv[1] == "commander":
        Item["host"] = {'S': sys.argv[3]}
        Item["user"] = {'S': sys.argv[4]}
        Item["port"] = {'S': sys.argv[5]}
        Item["check_command"] = {'S': sys.argv[6]}
        Item["requested_value"] = {'S': sys.argv[7]} # output is a string in fabric
        Item["fix_command"] = {'S': sys.argv[8]}
    elif sys.argv[1] == "ping":
        Item["host"] = {'S': sys.argv[3]}
        Item["timeout"] = {'S': sys.argv[4]}

        if len(sys.argv) > 5:
            Item["check_metric"] = {'S': sys.argv[5]}
            Item["check_value"] = {'S': sys.argv[6]}
            Item["check_operator"] = {'S': sys.argv[7]}
    elif sys.argv[1] == "metric":
        Item["host"] = {'S': sys.argv[3]}
        Item["user"] = {'S': sys.argv[4]}
        Item["port"] = {'S': sys.argv[5]}
        Item["metrics_name"] = {'S': sys.argv[7]}
        file = open(sys.argv[6])
        Item["metrics"] = {'S': file.read()}
    else:
        print("wrong type")
        return

    dynamodb.put_item(
    TableName='tuttofare_config',
    Item=Item
    )
    return

main()