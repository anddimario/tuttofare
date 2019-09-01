import requests
from dictor import dictor

def run(ping):
    notification_text = False
    status = False
    try:
        timeout = int(ping["timeout"]["S"])
        r = requests.get(ping["host"]["S"], timeout=timeout)
        status = r.status_code
        # check a metrics in response
        if "check_metric" in ping.keys() and status == 200:
            response_json = r.json()
            actual_value = dictor(response_json, ping["check_metric"]["S"])
            print(actual_value)
            if ping["check_operator"]["S"] == "=":
                if actual_value == ping["check_value"]["S"]:
                    status = "500 in = test"
            elif ping["check_operator"]["S"] == ">":
                if actual_value > ping["check_value"]["S"]:
                    status = "500 in > test"
            elif ping["check_operator"]["S"] == "<":
                if actual_value < ping["check_value"]["S"]:
                    status = "500 in < test"
            elif ping["check_operator"]["S"] == "!=":
                if actual_value != ping["check_value"]["S"]:
                    status = "500 in != test"
            else:
                status = 500


    except requests.exceptions.RequestException as e:
        status = e

    if status != 200:
        notification_text = ping["host"]["S"] + " status: " + str(status)
    return notification_text
