from fabric import Connection
import sys
import yaml
import slack

stream = open("./config.yaml", "r")
config = yaml.load(stream, Loader=yaml.FullLoader)

# connect
for server in config["servers"]:
    value = config["servers"][server]
    c = Connection(
        host=value["host"],
        user=value["user"],
        port=value["port"],
    )

    # run check command
    result = c.run(value["check_command"]).stdout.strip()
    
    notification_text = value["host"] + " result: " + result
    print(notification_text)

    # check condition
    if result != value["requested_value"]:
        # notify
        if value["notify"] is True:
            client = slack.WebClient(token=value["slack_token"])

            slack_response = client.chat_postMessage(
                channel=value["slack_channel"],
                text=notification_text)
            print(slack_response)
        # run custom command
        result = c.run(value["fix_command"])
