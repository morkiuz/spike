resource "aws_s3_bucket" "data_bucket" {
  bucket = "web-scrape-data-bucket"
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Purpose = "Web Scraping Data Storage"
  }
}
