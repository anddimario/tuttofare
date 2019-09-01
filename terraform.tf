#
# VARIABLES
#
variable "aws_region" {
  description = "AWS region to launch sample"
  default = "eu-west-1"
}

variable "docker_image" {}


#
# PROVIDER
#
provider "aws" {
  region = "${var.aws_region}"
}


#
# DATA
#

# retrieves the default vpc for this region
data "aws_vpc" "default" {
  default = true
}

# retrieves the subnet ids in the default vpc
data "aws_subnet_ids" "all" {
  vpc_id = "${data.aws_vpc.default.id}"
}

#
# RESOURCES
#

resource "aws_iam_role" "instance-role" {
  name = "aws-batch-tuttofare-role"
  path = "/BatchSample/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement":
    [
      {
          "Action": "sts:AssumeRole",
          "Effect": "Allow",
          "Principal": {
            "Service": "ec2.amazonaws.com"
          }
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "instance-role" {
  role = "${aws_iam_role.instance-role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "instance-role" {
  name = "aws-batch-tuttofare-role"
  role = "${aws_iam_role.instance-role.name}"
}

resource "aws_iam_role" "aws-batch-service-role" {
  name = "aws-batch-service-role"
  path = "/BatchSample/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement":
    [
      {
          "Action": "sts:AssumeRole",
          "Effect": "Allow",
          "Principal": {
            "Service": "batch.amazonaws.com"
          }
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws-batch-service-role" {
  role = "${aws_iam_role.aws-batch-service-role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_security_group" "tuttofare-batch" {
  name = "aws-batch-tuttofare-security-group"
  description = "AWS Batch Sample Security Group"
  vpc_id = "${data.aws_vpc.default.id}"

  egress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    cidr_blocks     = [ "0.0.0.0/0" ]
  }
}

resource "aws_batch_compute_environment" "tuttofare" {
  compute_environment_name = "tuttofare"
  compute_resources {
    instance_role = "${aws_iam_instance_profile.instance-role.arn}"
    instance_type = [
      "optimal"
    ]
    max_vcpus = 2
    min_vcpus = 0
    security_group_ids = [
      "${aws_security_group.tuttofare-batch.id}"
    ]
    subnets = [
      "${data.aws_subnet_ids.all.ids}"
    ]
    type = "EC2"
  }
  service_role = "${aws_iam_role.aws-batch-service-role.arn}"
  type = "MANAGED"
  depends_on = [ "aws_iam_role_policy_attachment.aws-batch-service-role" ]
}

resource "aws_batch_job_queue" "tuttofare" {
  name = "tuttofare-queue"
  state = "ENABLED"
  priority = 1
  compute_environments = [ 
    "${aws_batch_compute_environment.tuttofare.arn}"
  ]
}

resource "aws_iam_role" "job-role" {
  name = "aws-batch-tuttofare-job-role"
  path = "/BatchSample/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement":
    [
      {
          "Action": "sts:AssumeRole",
          "Effect": "Allow",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          }
      }
    ]
}
EOF
}

resource "aws_batch_job_definition" "tuttofare-job" {
  name = "tuttofare-job"
  type = "container"
  container_properties = <<CONTAINER_PROPERTIES
{
  "image": "${var.docker_image}", 
  "jobRoleArn": "${aws_iam_role.job-role.arn}",
  "vcpus": 1,
  "memory": 256,
  
  "command": [
    "pipenv",
    "run",
    "python",
    "tuttofare.py"
  ]
}
CONTAINER_PROPERTIES
}


### LAMBDA
# helper to package the lambda function for deployment
data "archive_file" "lambda_zip" {
  type = "zip"
  source_file = "cron/index.js"
  output_path = "lambda_function.zip"
}

## lambda resource + iam
resource "aws_iam_role" "lambda-role" {
  name = "tuttofare-function-role"
  path = "/BatchSample/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement":
    [
      {
          "Action": "sts:AssumeRole",
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          }
      }
    ]
}
EOF
}

resource "aws_iam_policy" "lambda-policy" {
  name = "tuttofare-function-policy"
  path = "/BatchSample/"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "batch:SubmitJob"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda-service" {
  role = "${aws_iam_role.lambda-role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda-policy" {
  role = "${aws_iam_role.lambda-role.name}"
  policy_arn = "${aws_iam_policy.lambda-policy.arn}"
}

resource "aws_lambda_function" "submit-job-function" {
  function_name = "tuttofare-cron-function"
  filename = "lambda_function.zip"
  role = "${aws_iam_role.lambda-role.arn}"
  handler = "index.handler"
  source_code_hash = "${data.archive_file.lambda_zip.output_base64sha256}"
  runtime = "nodejs8.10"
  depends_on = [ "aws_iam_role_policy_attachment.lambda-policy" ]
  environment = {
    variables = {
      JOB_DEFINITION = "${aws_batch_job_definition.image-processor-job.arn}"
      JOB_QUEUE = "${aws_batch_job_queue.image-processor.arn}"
      IMAGES_BUCKET = "${aws_s3_bucket.image-bucket.id}"
      IMAGES_TABLE = "${aws_dynamodb_table.image-table.id}"
    }
  }
}
# cron
resource "aws_cloudwatch_event_rule" "every_hour" {
    name = "every_hour"
    description = "Fires every hour"
    schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "send_job_every_hour" {
    rule = "${aws_cloudwatch_event_rule.every_hour.name}"
    target_id = "send_job_test"
    arn = "${aws_lambda_function.submit-job-function.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_send_job_test" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.submit-job-function.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.every_hour.arn}"
}

### DYNAMODB
resource "aws_dynamodb_table" "tuttofare_config" {
  name         = "tuttofare_config"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}
resource "aws_dynamodb_table" "tuttofare_metrics" {
  name         = "tuttofare_config"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

