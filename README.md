# The Scræper
This project uses AWS and Python.

IMG


## Working principle
A list of domains is submitted to SQS, SQS then invokes Lambdas for scraping the URLs which then uploads the scraped content to S3 bucket and creates new SQS messages for discovered URLs which were under the same domain. This implements a dynamic scraper which should be bound within the domains provided and not take down the entire data center by their exponential growth. 