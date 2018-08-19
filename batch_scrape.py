import logging
import requests
import concurrent.futures
from collections import namedtuple
from bs4 import BeautifulSoup
import feedparser

NewsContent = namedtuple('NewsContent', 'title, text')
LOGGER = logging.getLogger(__name__)


def get_news_from_page(data: str) -> NewsContent:
    '''Get news from a reuters page'''
    soup = BeautifulSoup(data, 'html.parser')
    headline = soup.find('h1').string
    article_content = soup.find_all('p')
    text_arr = [p.string for p in article_content if p.string is not None]
    text = '.'.join(text_arr)
    news_content = NewsContent(
        title=headline,
        text=text
    )
    return news_content


class Reuters:

    _RSS_URL = 'http://feeds.reuters.com/Reuters/worldNews'

    def __init__(self):
        self._scraping_func = get_news_from_page

    def get_feed(self):
        '''Read rss feed from reuters'''
        parsed = feedparser.parse(self._RSS_URL)
        return parsed.entries

    def scrape(self):
        '''Scrape multiple links from reuters'''

        def _load_url(url):
            return requests.get(url)

        links = self._get_links()

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_url = {executor.submit(_load_url, url) : url for url in links}

            result = []
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result().content
                except requests.exceptions.RequestException:
                    LOGGER.error('Something went wrong processing request %s', url)
                    continue
                news = self._scraping_func(data)
                result.append(news)

        return result

    def _get_links(self):
        feed = self.get_feed()
        links = set([f.link for f in feed])
        return links
