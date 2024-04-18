resource "aws_lambda_function" "scrape_function" {
  function_name = "web_scrape_function"
  handler       = "scraper.handler"
  runtime       = "python3.9"

  filename      = "$../function.zip"

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.url_table.name
      SQS_QUEUE_URL  = aws_sqs_queue.web_scrape_queue.url
      S3_BUCKET      = aws_s3_bucket.data_bucket.bucket
      DLQ_QUEUE_URL = aws_sqs_queue.web_scrape_dlq.url
    }
  }

  role = aws_iam_role.lambda_exec_role.arn
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  role   = aws_iam_role.lambda_exec_role.id
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "s3:PutObject"]
    resources = [aws_dynamodb_table.url_table.arn, aws_s3_bucket.data_bucket.arn]
  }
}
