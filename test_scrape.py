'''Test scraping reuters website'''
import pytest
from batch_scrape import Reuters, NewsContent

@pytest.fixture(scope='module')
def reuters():
    return Reuters()


def test_get_feed(reuters):
    feed = reuters.get_feed()
    assert isinstance(feed, list)


def test_scrape(reuters):
    scraped = reuters.scrape()
    assert isinstance(scraped, list)
    assert len(scraped) > 0
    assert all(isinstance(f, NewsContent) for f in scraped)
