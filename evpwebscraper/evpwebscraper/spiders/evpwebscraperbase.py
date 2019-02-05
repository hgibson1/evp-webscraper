# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

#from evpwebscraper.items import EvpwebscraperItem
from .. conf import *
from .. helper_functions import *

class EvpwebscraperbaseSpider(scrapy.Spider):
    name = 'evpwebscraperbase'
    towns = read_in_data(DATA_FILE_IN)
    start_urls = [row[HEADERS['website']] for row in towns]
    allowed_domains = [urlparse(url).netloc for url in start_urls]
    keys = [
        re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}") # Regex for phone num
    ]

    def start_requests(self):
        # Attach and index to the requests
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'index': index})

    def parse(self, response):
        # Check status code

        # Create new Item with contents of response
        #item = EvpwebscraperItem()
        #item['raw_html'] = response.text
        # Find coresponding town
        #item['town'] = self.towns[town_index][HEADERS['town']]
        # Pass item to processing pipeline
        #yield item
        html = BeautifulSoup(response.text, 'lxml')
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        # Clean up remaining text and look for phone numbers
        # Phone numbers will be in string format number;number
        lines = [line.lower() for line in html.stripped_strings if any(key.match(line.lower()) for key in self.keys)]
        phone = ';'.join(lines)

