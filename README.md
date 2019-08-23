Execute check on servers using aws batch and aws lambda (as cron for aws batch job launcher)

### Requirments
- terraform
- an aws account
- an iam user with admin role
- slack app with api tokens for notifications (optional)

### Install
- in `cron/` run: `npm install`
- create a `config.yaml` based on `config.yaml.example`
- create an ssh key (used to connect to hosts) in the relive directory: `ssh-keygen - f relive`
- then start terraform
```
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="..."
export AWS_REGION="..."
export TF_VAR_docker_image=your_ecr_image_path
terraform apply
```

### Dev Requirements
- [pipenv](https://github.com/pypa/pipenv/)
- docker

### Localhost run with docker
- go in the project root
- create the `config.yaml`
- build the image: `docker build -t relive .`
- run the image: `docker run --network="host" -t relive`