# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from . conf import keywords, websites

class ElectionCrawlerSpider(CrawlSpider):
    name = 'election_crawler'
    start_urls = websites
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
                line.lower() for line in html.stripped_strings if any(keyword in line.lower() for keyword in keywords)
        ]
        text = ''.join(lines)
        print(text)
        # Find links
        hrefs = [Request(response.urljoin(a['href'])) for a in html.find_all('a', href=True)]
        return hrefs

