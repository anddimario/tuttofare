Get metrics, run commands, parse logs and do checks on servers using aws. Services used:
- batch: to run docker container as job
- lambda: as cron for aws batch job launcher
- dynamodb: store config and metrics data
- kinesis+s3: store parsed logs

### Features
- serverless
- run commands on remote servers and execute command based on the results
- check response status code
- check field in json response
- get custom metrics from remote servers and store on dynamodb
- interval from the last execution
- parse log and store on s3 (available type: nginx access log and syslog)
- add/remove action for dynamic resources
- notify on slack (optional)

### Requirments
- terraform
- an aws account
- an iam user with admin role
- slack app with api tokens for notifications (optional)

### Install
- create an iam user with access on s3 and dynamodb
- in `cron/` run: `npm install`
- create a `config.yaml` with:
```
aws:
  ACCESS_KEY: ....
  SECRET_KEY: ....
  REGION: ....
  DYNAMODB_ENDPOINT: ...
  KINESIS_ENDPOINT: ...
  KINESIS_STREAM: 
    nginx: ...
    syslog: ...
slack:
  notify: false/true
  token: ...
  channel: ...

```
- create an ssh key (used to connect to hosts) in the tuttofare directory: `ssh-keygen -f tuttofare`
- build the image and send to ecr: 
```
docker build -t tuttofare .
$(aws ecr get-login --no-include-email --region eu-west-1)
docker tag tuttofare MY_ECR/MY_WORKSPACE:tuttofare
docker push MY_ECR/MY_WORKSPACE:tuttofare
```
- then start terraform
```
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="..."
export AWS_REGION="..."
export TF_VAR_docker_image=your_ecr_image_path
export TF_VAR_bucket_name=your_bucket_name
terraform apply
```
- add a config on dynamo (see next sessions)

### Create a config 
#### Commander
```
python scripts/add_config.py commander INTERVAL HOST USER PORT CHECK_COMMAND REQUESTED_VALUE FIX_TYPE FIX_SCRIPT
example: python scripts/add_config.py commander 1 localhost root 32768 "ps aux | grep ssh | wc -l" 4 command "echo ciao"
```
**Notes:**
- `INTERVAL` is in minutes, if 0 the actions is done on every batch, otherwise is run if interval from the last execution is higher than the value
- `FIX_TYPE`: script or command
- `FIX_SCRIPT`: if script, it's a path where python script is stored and this script is launched as exec(). If command, run the command on remote host

#### Ping
```
python scripts/add_config.py ping INTERVAL URL TIMEOUT
python scripts/add_config.py ping INTERVAL URL TIMEOUT CHECK_METRIC CHECK_VALUE CHECK_OPERATOR
example: python scripts/add_config.py ping 1 "http://www.example.com" 10
example with check metric from json: python scripts/add_config.py 1 ping "http://www.example.com/json" 10 "my.text.metric" 100 "="
```
**Notes:**
- `INTERVAL` is in minutes, if 0 the actions is done on every batch, otherwise is run if interval from the last execution is higher than the value
- `CHECK_OPERATOR` could be =, >, <, != operators supported in python
- `CHECK_METRIC` support the form: https://medium.com/@mike.reider/python-dictionaries-get-nested-value-the-sane-way-4052ab99356b

#### Metric
```
python scripts/add_config.py metric INTERVAL HOST USER PORT FILE METRICS_NAMES
example: python scripts/add_config.py metric 1 localhost root 32768 metrics.txt "USEDMEMORY,TCP_CONN,TCP_CONN_PORT_80,USERS"
```
metrics.txt example:
```
free -m | awk 'NR==2{printf "%.2f\t", $3*100/$2 }'
netstat -an | wc -l
netstat -an | grep 80 | wc -l
uptime |awk '{ print $4 }'
```
**Notes:**
- `INTERVAL` is in minutes, if 0 the actions is done on every batch, otherwise is run if interval from the last execution is higher than the value
- `METRICS_NAMES` must have the same order that have command in `metrics.txt`
#### Parser
```
python scripts/add_config.py parse INTERVAL HOST USER PORT FILE_PATH FILE_TYPE OPTIONAL_COMMAND
example: python scripts/add_config.py parse 1 localhost root 32768 "/var/log/syslog" syslog 
```
**Notes:**
- `INTERVAL` is in minutes, if 0 the actions is done on every batch, otherwise is run if interval from the last execution is higher than the value
- `FILE_TYPE`: available type: `syslog` and `nginx` access log
- `OPTIONAL_COMMAND`: not required, if present, run a command after log get from server, useful for example for log rotation

## Dev 
### Requirements
- [pipenv](https://github.com/pypa/pipenv/)
- docker and docker compose
- [localstack](https://github.com/localstack/localstack)

### Build on localhost
- go in the project root
- build the image: `docker build -t tuttofare .`
- run the image: `docker run --network="host" -t tuttofare`

### Run localstack
```
export SERVICES=s3,dynamodb,firehose
docker-compose up
```

### Create resources on localstack
In `terraform/dev`:
```
export TF_VAR_bucket_name=your_bucket_name
terraform apply
```
**NOTES**: on dev localstack there's not lambda and batch, so run batch as a docker container for tests

#### Userful aws cli commands
```
aws s3 --endpoint=http://localhost:4572 mb s3://testLocalhost
aws dynamodb  --endpoint=http://localhost:4569 create-table --table-name tuttofare_config --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
aws dynamodb  --endpoint=http://localhost:4569 create-table --table-name tuttofare_metrics --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
aws dynamodb  --endpoint=http://localhost:4569 get-item --table-name tuttofare_metrics --key file://get.json
aws firehose --endpoint=http://localhost:4573 create-delivery-stream --delivery-stream-name tuttofare --extended-s3-destination-configuration
aws dynamodb  --endpoint=http://localhost:4569 list-tables
aws firehose --endpoint=http://localhost:4573 describe-delivery-stream --delivery-stream-name tuttofare_kinesis
```

### Run an ssh container
Thanks: https://hub.docker.com/r/rastasheep/ubuntu-sshd/
```
docker run -d -P --name test_sshd rastasheep/ubuntu-sshd:18.04
docker port test_sshd 22
  0.0.0.0:49154

$ ssh root@localhost -p 49154
# The password is `root`
root@test_sshd $
```

### License
MIT
