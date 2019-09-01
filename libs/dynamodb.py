import boto3
from datetime import datetime, time


def get_all(config_aws):
    #  get config servers from dynamo
    dynamodb = boto3.client(
        'dynamodb',
        aws_access_key_id=config_aws["ACCESS_KEY"],
        aws_secret_access_key=config_aws["SECRET_KEY"],
        region_name=config_aws["REGION"],
        # use localstack: http://localhost:4569
        endpoint_url=config_aws["DYNAMODB_ENDPOINT"],
    )
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Paginator.Scan
    paginator = dynamodb.get_paginator('scan')
    page_iterator = paginator.paginate(
        TableName='tuttofare_config',
    )
    items = []
    for page in page_iterator:
        items += page['Items']
    return items


def store_last_execution(config_aws, item_id):
    now = datetime.now()
    #  get config servers from dynamo
    dynamodb = boto3.client(
        'dynamodb',
        aws_access_key_id=config_aws["ACCESS_KEY"],
        aws_secret_access_key=config_aws["SECRET_KEY"],
        region_name=config_aws["REGION"],
        # use localstack: http://localhost:4569
        endpoint_url=config_aws["DYNAMODB_ENDPOINT"],
    )
    dynamodb.update_item(
        TableName='tuttofare_config',
        Key={'id': item_id},
        UpdateExpression='SET last_execution = :now',
        ExpressionAttributeValues={
            ':now': {'S': str(now)}
        }
    )
    return
