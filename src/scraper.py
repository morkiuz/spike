import logging
import boto3
from requests_html import HTMLSession
import os
from bs4 import BeautifulSoup
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DATA_BUCKET = os.getenv("S3_BUCKET")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
DQL_QUEUE_URL = os.getenv("DLQ_QUEUE_URL")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

dynamodb = None
s3 = None
sqs = None


def get_dynamodb_client():
    global dynamodb_client
    if dynamodb_client is None:
        dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")


def get_s3_client():
    global s3_client
    if s3_client is None:
        s3_client = boto3.client("s3", region_name="us-east-1")


def get_sqs_client():
    global sqs_client
    if sqs_client is None:
        sqs_client = boto3.client("sqs", region_name="us-east-1")


def enqueue_urls(urls: set):
    for url in urls:
        sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=url)


def send_to_dlq(message_body: str) -> None:
    sqs.send_message(QueueUrl=DQL_QUEUE_URL, MessageBody=message_body)


def check_if_scraped(url: str) -> bool:
    response = dynamodb.get_item(TableName="ScrapedUrls", Key={"URL": {"S": url}})
    return "Item" in response


def scrape_website(url: str) -> tuple[str, set[str]]:
    session = HTMLSession()
    response = session.get(url)

    response.html.render()  # Render JavaScript in case of CF challenge, might be resource-intensive, needs testing + optimizing

    soup = BeautifulSoup(response.content, "html.parser")
    domain = urllib.parse.urlparse(url).netloc
    found_urls = {
        urllib.parse.urljoin(url, tag["href"])
        for tag in soup.find_all("a", href=True)
        if urllib.parse.urlparse(tag["href"]).netloc == domain
    }

    return response.text, found_urls


def save_to_s3(url: str, content: str) -> None:
    s3.put_object(
        Bucket=DATA_BUCKET,
        Key=f"data/{url.replace('/', '_')}.html",
        Body=content,
    )


def mark_url_as_scraped(url: str) -> None:
    dynamodb.put_item(TableName=DYNAMODB_TABLE, Item={"URL": {"S": url}})


def handler(event, context):
    get_dynamodb_client(), get_s3_client(), get_sqs_client()
    for record in event["Records"]:
        url = record["body"]
        if not check_if_scraped(url):
            try:
                content, found_urls = scrape_website(url)
                save_to_s3(url, content)
                mark_url_as_scraped(url)
                enqueue_urls(found_urls)
            except (
                Exception
            ) as e:  # in production we would catch specific exceptions to handle specific cases and function errors
                logger.error(f"Error processing URL {url}: {str(e)}")
                send_to_dlq(url)
                continue
        else:
            logger.info(f"URL already scraped: {url}")
