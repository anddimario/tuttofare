from fabric import Connection


def run(server):
    notification_text = False
    # connect
    c = Connection(
        host=server["host"]["S"],
        user=server["user"]["S"],
        port=server["port"]["S"],
    )

    # run check command
    # hide output: https://github.com/fabric/fabric/issues/1811
    result = c.run(server["check_command"]["S"], hide=True).stdout.strip()

    c.close()
    # check condition
    if result != server["requested_value"]["S"]:
        notification_text = server["host"]["S"] + " result: " + result
        # run custom command
        result = c.run(server["fix_command"]["S"])
    return notification_text
