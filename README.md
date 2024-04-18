# The Scræper
This project uses AWS and Python.

IMG


## Working principle
A list of domains is submitted to SQS, SQS then invokes Lambdas for scraping the URLs which then uploads the scraped content to S3 bucket and creates new SQS messages for discovered URLs which were under the same domain. This implements a dynamic scraper which should be bound within the domains provided and not take down the entire data center by their exponential growth. 

## Limitations
-> The main limit here is introduced in the event_source_mapping where we set batch size to 50. This can be adjusted as needed.
-> Timeouts should not be an issue as max is around 15 mins.
-> There is a bit of overhead with having a single lambda scraping a single page at a time, this can potentially be optimized.

