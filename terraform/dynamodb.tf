resource "aws_dynamodb_table" "url_table" {
  name           = "ScrapedUrls"
  billing_mode   = "PROVISIONED"
  read_capacity  = var.dynamodb_table_read_capacity
  write_capacity = var.dynamodb_table_write_capacity
  hash_key       = "URL"

  attribute {
    name = "URL"
    type = "S"
  }

  tags = {
    Name = "ScrapedUrls"
  }
}
