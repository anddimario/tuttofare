from fabric import Connection
import re
import boto3
from libs import utils
import json


# Yield successive n-sized 
# chunks from l. 
# https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def run(server, config_aws):
    # connect
    c = Connection(
        host=server["host"]["S"],
        user=server["user"]["S"],
        port=server["port"]["S"],
    )

    # get file
    # hide output: https://github.com/fabric/fabric/issues/1811
    result = c.run('cat ' + server["file_path"]
                   ["S"], hide=True).stdout.strip().split('\n')

    # optional command
    if "optional_command" in server.keys():
        c.run(server["optional_command"]["S"], hide=True)
    c.close()

    json_lines = []
    firehose_stream = ""
    # parse by line
    if server["file_type"]["S"] == "syslog":
        parser_syslog = utils.SyslogParser()
        # thanks: https://gist.github.com/leandrosilva/3651640
        lineformat = re.compile(
            r"""(?P<month>\S+) - (?P<date>[0-9]{1,2})""", re.IGNORECASE)
        for l in result:
            fields = parser_syslog.parse(l)
            json_lines.append(fields)
        firehose_stream = config_aws["KINESIS_STREAM"]["syslog"]
    elif server["file_type"]["S"] == "nginx":
        # thanks: https://gist.github.com/hreeder/f1ffe1408d296ce0591d
        lineformat = re.compile(
            r"""(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - (?P<remoteuser>.+) \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(?P<method>.+) )(?P<url>.+)(http\/[1-2]\.[0-9]")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["])""", re.IGNORECASE)

        for l in result:
            data = re.search(lineformat, l)
            if data:
                data = data.groupdict()
                # Transform in byte as requested
                data_as_bytes = json.dumps(data, indent=2).encode('utf-8')
                # Create the record as requested and append, see: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/firehose.html#Firehose.Client.put_record_batch
                json_lines.append({"Data": data_as_bytes})

        firehose_stream = config_aws["KINESIS_STREAM"]["nignx"]

    else:
        return

    # send to kinesis
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/firehose.html
    firehose = boto3.client(
        'firehose',
        aws_access_key_id=config_aws["ACCESS_KEY"],
        aws_secret_access_key=config_aws["SECRET_KEY"],
        region_name=config_aws["REGION"],
        # use localstack: http://localhost:4569
        endpoint_url=config_aws["KINESIS_ENDPOINT"],
    )
    # split records, max is 500 for boto
    n = 500
    splitted_records = list(divide_chunks(json_lines, n)) 
    for splitted_record in splitted_records:
        print(len(splitted_record))
        firehose.put_record_batch(
            DeliveryStreamName=firehose_stream,
            Records=splitted_record
        )

    return
