resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  event_source_arn = aws_sqs_queue.web_scrape_queue.arn
  function_name    = aws_lambda_function.scrape_function.arn
  batch_size       = 50 # should be high enough to work and not get us banned 
  on_failure {
    destination_arn = aws_sqs_queue.web_scrape_dlq.arn
  }
}
