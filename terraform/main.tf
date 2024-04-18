provider "aws" {
  region = "us-east-1"
}

variable "lambda_deployment_key" {
  description = "The S3 key for the Lambda deployment package."
  type        = string
}

variable "dynamodb_table_read_capacity" {
  description = "Read capacity units for the DynamoDB table."
  default     = 100
}

variable "dynamodb_table_write_capacity" {
  description = "Write capacity units for the DynamoDB table."
  default     = 100
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}
