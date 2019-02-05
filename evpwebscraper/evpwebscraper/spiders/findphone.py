# -*- coding: utf-8 -*-
import scrapy
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from csv import DictWriter

from .. conf import *
from .. helper_functions import *

logger = logging.getLogger()

class FindphoneSpider(scrapy.Spider):
    name = 'findphone'
    towns = read_in_data(DATA_FILE_IN)
    start_urls = [row[HEADERS['website']] for row in towns]
    allowed_domains = [urlparse(url).netloc for url in start_urls]
    keys = [
        re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}") # Regex for phone num
    ]

    def start_requests(self):
        # Create output csvfile and write headers
        with open(DATA_FILE_OUT, 'w') as csvfile:
            csvwriter = DictWriter(csvfile, fieldnames=[HEADERS[key] for key in HEADERS.keys()])
            csvwriter.writeheader()
        # Attach and index to the requests
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'index': index})

    def parse(self, response):
        # Check status code

        # Get index
        town_index = response.meta['index']
        logger.info(self.towns[town_index])
        # Get html 
        html = BeautifulSoup(response.text, 'lxml')
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        # Clean up remaining text and look for phone numbers
        # Phone numbers will be in string format number;number
        lines = [line.lower() for line in html.stripped_strings if any(key.match(line.lower()) for key in self.keys)]
        phone = ';'.join(lines)
        self.towns[town_index][HEADERS['phone']] = phone
        # Log data
        logger.info(self.towns[town_index])
        # Write data to csv file
        with open(DATA_FILE_OUT, 'a') as csvfile:
            csvwriter = DictWriter(csvfile, fieldnames=[HEADERS[key] for key in HEADERS.keys()])
            csvwriter.writerow(self.towns[town_index])

