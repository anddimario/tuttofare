#
# VARIABLES
#
variable "aws_region" {
  description = "AWS region to launch sample"
  default     = "eu-west-1"
}

variable "bucket_name" {}

#
# PROVIDER
#
provider "aws" {
  region = "${var.aws_region}"

  # https://www.terraform.io/docs/providers/aws/guides/custom-service-endpoints.html#localstack
  endpoints {
    dynamodb = "http://localhost:4569"
    s3       = "http://localhost:4572"
    firehose = "http://localhost:4573"
    lambda   = "http://localhost:4574"
  }
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
  name         = "tuttofare_metrics"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

### S3
resource "aws_s3_bucket" "tuttofare_s3" {
  bucket = "${var.bucket_name}"
  acl    = "private"

  tags = {
    Name = "TuttoFare Bucket"
  }
}

### KINESIS
resource "aws_kinesis_firehose_delivery_stream" "tuttofare_kinesis" {
  name        = "tuttofare_kinesis"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = "arn:aws:iam::817386470555:role/firehose_delivery_role"
    bucket_arn = "arn:aws:s3:::${aws_s3_bucket.tuttofare_s3.bucket}"

    compression_format = "GZIP"

    processing_configuration {
      enabled = "false"
    }
  }
}
