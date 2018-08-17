import logging
import requests
import concurrent.futures
from collections import namedtuple
from bs4 import BeautifulSoup
import feedparser


# Define datatypes
NewsContent = namedtuple('NewsContent', 'title, text')

LOGGER = logging.getLogger(__name__)


class Reuters:

    _RSS_URL = 'http://feeds.reuters.com/Reuters/worldNews'

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
                    data = future.result()
                    soup = BeautifulSoup(data, 'html.parser')
                    result.append(soup.findAll('h2'))
                    LOGGER.error(soup)
                except Exception as exec:
                    LOGGER.error('Something wrong happened getting %s', url)

        return result

    def _get_links(self):
        feed = self.get_feed()
        links = set([f.link for f in feed])
        return links
