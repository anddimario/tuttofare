from fabric import Connection
import datetime
import uuid
import boto3

def run(server, config_aws):

    dynamodb = boto3.client(
        'dynamodb',
        aws_access_key_id=config_aws["ACCESS_KEY"],
        aws_secret_access_key=config_aws["SECRET_KEY"],
        region_name=config_aws["REGION"],
        endpoint_url=config_aws["DYNAMODB_ENDPOINT"], # use localstack: http://localhost:4569
    )

    # connect
    c = Connection(
        host=server["host"]["S"],
        user=server["user"]["S"],
        port=server["port"]["S"],
    )

    metrics = server["metrics"]["S"].split("\n")
    metrics_name = server["metrics_name"]["S"].split(",")

    item = {
        'id': {'S': str(uuid.uuid4())},
        'metric_id': server["id"],
        'date': {'S': str(datetime.datetime.now())}
    }
    # run command
    # hide output: https://github.com/fabric/fabric/issues/1811
    for i, metric in enumerate(metrics):
        if metric != "":
            result = c.run(metric, hide=True).stdout.strip()
            if result != "":
                item[metrics_name[i]] = {'S': result}

    c.close()

    # store in dynamodb
    dynamodb.put_item(
        TableName='tuttofare_metrics',
        Item=item
    )
    return
