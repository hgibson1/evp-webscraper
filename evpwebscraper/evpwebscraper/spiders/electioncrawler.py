# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .. conf import *
from .. helper_functions import *

class ElectionCrawlerSpider(CrawlSpider):
    name = 'election_crawler'
    keywords = ['election']
    towns = read_in_data(DATA_FILE_IN)
    start_urls = [row[HEADERS['website']] for row in towns]
    domains = [urlparse(url).netloc for url in start_urls]
    rules = [
        Rule(LinkExtractor(allow_domains=(domains)), follow=True, callback='parse')
    ]

    def parse(self, response):
        # Extract all webpage text
        html = BeautifulSoup(response.text, 'lxml')
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        # Clean up remaining text and look for keywords
        lines = [
                line.lower() for line in html.stripped_strings if any(keyword in line.lower() for keyword in self.keywords)
        ]
        text = ''.join(lines)
        print(text)
        # Find links
        hrefs = [Request(response.urljoin(a['href'])) for a in html.find_all('a', href=True)]
        return hrefs

