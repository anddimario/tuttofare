from executors import commander, ping, metric, parser
from libs import dynamodb, utils
import slack
import yaml

stream = open("./config.yaml", "r")
config = yaml.load(stream, Loader=yaml.FullLoader)

items = dynamodb.get_all(config["aws"])

# initialize slack client
if config["slack"]["notify"] is True:
    client = slack.WebClient(token=config["slack"]["token"])

for item in items:
    # check if can execute
    if int(item["interval"]["S"]) > 0:
        diff_last_execution = utils.date_diff_in_seconds(item["last_execution"]["S"])
        if diff_last_execution < int(item["interval"]["S"]):
            continue

    notification_text = False
    if item["tuttofare_type"]["S"] == "commander":
        notification_text = commander.run(item)
    elif item["tuttofare_type"]["S"] == "ping":
        notification_text = ping.run(item)
    elif item["tuttofare_type"]["S"] == "metric":
        metric.run(item, config["aws"])
    elif item["tuttofare_type"]["S"] == "parse":
        parser.run(item, config["aws"])

    # if interval != 0, set last execution on dynamo
    if int(item["interval"]["S"]) > 0:
        dynamodb.store_last_execution(config["aws"], item["id"])

    # notify on slack
    if config["slack"]["notify"] is True and notification_text is not False:
        slack_response = client.chat_postMessage(
            channel=config["slack"]["channel"],
            text=notification_text)

    if notification_text is not False:
        # print logs
        print(notification_text)
