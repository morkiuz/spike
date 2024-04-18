import pytest
from unittest.mock import Mock, patch
from src.scraper import handler, enqueue_urls, send_to_dlq, scrape_website
from requests_html import HTMLSession


@pytest.mark.parametrize(
    "url, html_content, expected_content, expected_urls",
    [
        (
            "http://example.com",
            "<html><body><a href='http://example.com/about'>About</a><a href='http://example.com/contact'>Contact</a></body></html>",
            "Example content",
            {"http://example.com/about", "http://example.com/contact"},
        ),
        (
            "http://test.com",
            "<html><body><a href='http://test.com/info'>Info</a></body></html>",
            "Test content",
            {"http://test.com/info"},
        ),
    ],
)
def test_scrape_website(mocker, url, html_content, expected_content, expected_urls):
    mock_response = Mock()
    mock_response.content = html_content.encode("utf-8")  # Ensure bytes
    mock_response.text = expected_content
    mocker.patch.object(HTMLSession, "get", return_value=mock_response)

    content, urls = scrape_website(url)

    assert content == expected_content
    assert urls == expected_urls


@pytest.mark.parametrize(
    "urls",
    [
        ({"http://example.com/page1", "http://example.com/page2"}),
        ({"http://test.com/home"}),
    ],
)
def test_enqueue_urls(mocker, urls):
    mock_sqs_client = mocker.patch("src.scraper.sqs", return_value=mocker.Mock())
    mock_sqs_client.send_message = mocker.Mock()

    enqueue_urls(urls)

    assert mock_sqs_client.send_message.call_count == len(urls)


def test_send_to_dlq(mocker):
    mock_sqs_client = mocker.patch("src.scraper.sqs", return_value=mocker.Mock())
    mock_sqs_client.send_message = mocker.Mock()

    send_to_dlq("http://failed.com")

    mock_sqs_client.send_message.assert_called_once()


@pytest.mark.parametrize(
    "records, already_scraped, expected_calls",
    [
        ([{"body": "http://example.com"}], False, 1),
        ([{"body": "http://already_scraped.com"}], True, 0),
    ],
)
def test_handler(mocker, records, already_scraped, expected_calls):
    mocker.patch(
        "src.scraper.check_if_scraped",
        return_value=already_scraped,
    )
    mocker.patch(
        "src.scraper.scrape_website",
        return_value=("Content", {"http://example.com/contact"}),
    )
    mocker.patch("src.scraper.save_to_s3")
    mocker.patch("src.scraper.mark_url_as_scraped")
    mocker.patch("src.scraper.send_to_dlq")
    mocker.patch("src.scraper.get_dynamodb_client")
    mocker.patch("src.scraper.get_s3_client")
    mocker.patch("src.scraper.get_sqs_client")
    enqueue_urls = mocker.patch("src.scraper.enqueue_urls")
    mock_event = {"Records": records}

    handler(mock_event, None)

    assert enqueue_urls.call_count == expected_calls
