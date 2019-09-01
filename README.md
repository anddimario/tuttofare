Get metrics, run commands and do checks on servers using aws. Services used:
- batch: to run docker container as job
- lambda: as cron for aws batch job launcher
- dynamodb: store config and metrics data

### Features
- serverless
- run commands on remote servers and execute command based on the results
- check response status code
- check field in json response
- get custom metrics from remote servers and store on dynamodb
- interval from the last execution
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
slack:
  notify: false/true
  token: ...
  channel: ...

```
- create an ssh key (used to connect to hosts) in the tuttofare directory: `ssh-keygen -f tuttofare`
- then start terraform
```
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="..."
export AWS_REGION="..."
export TF_VAR_docker_image=your_ecr_image_path
terraform apply
```
- add a config on dynamo (see next sessions)

### Create a config 
#### Commander
```
python scripts/add_config.py commander INTERVAL HOST USER PORT CHECK_COMMAND REQUESTED_VALUE FIX_COMMAND
example: python scripts/add_config.py commander 1 localhost root 32768 "ps aux | grep ssh | wc -l" 4 "echo ciao"
```
**Notes:**
- `INTERVAL` is in minutes, if 0 the actions is done on every batch, otherwise is run if interval from the last execution is higher than the value
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
export SERVICES=s3,dynamodb
docker-compose up
```

### Create resources on localstack
```
aws s3 --endpoint=http://localhost:4572 mb s3://testLocalhost
aws dynamodb  --endpoint=http://localhost:4569 create-table --table-name tuttofare_config --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
aws dynamodb  --endpoint=http://localhost:4569 create-table --table-name tuttofare_metrics --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
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
