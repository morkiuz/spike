resource "aws_sqs_queue" "web_scrape_queue" {
  name                      = "web-scrape-queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.web_scrape_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "web_scrape_dlq" {
  name = "web-scrape-dlq"
}
