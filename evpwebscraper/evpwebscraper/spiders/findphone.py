# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from csv import DictReader

from . conf import *
from . helper_functions import *


class FindphoneSpider(scrapy.Spider):
    name = 'findphone'
    keys = [
        #re.compile("phone"), 
        re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}") # Regex for phone num
    ]
    towns = read_in_data(DATA_FILE_IN)
    start_urls = [row[HEADERS['website']] for row in towns]
    allowed_domains = [urlparse(url).netloc for url in start_urls]

    def start_requests(self):
        # Attach and index to the requests
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'index': index})

    def parse(self, response):
        # Extract all webpage text
        html = BeautifulSoup(response.text, 'lxml')
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        # Clean up remaining text and look for phone numbers
        # Phone numbers will be in string format number;number
        lines = [line.lower() for line in html.stripped_strings if any(key.match(line.lower()) for key in self.keys)]
        text = ';'.join(lines)
        # Find coresponding town
        town_index = response.meta['index']
        self.towns[town_index][HEADERS['phone']] = text

    def spider_closed(self, spider):
        write_out_data(DATA_OUT_FILE, [HEADERS[key] for key in HEADERS], self.towns)

