# -*- coding: utf-8 -*-
import scrapy
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

from .. conf import *
from .. helper_functions import *

def filter_text(text):
    pattern = re.compile("\(?[0-9]{3}\)?(\s|-|\.)*\(?[0-9]{3}\)?(\s|-|\.)*\(?[0-9]{4}\)?") # Regex for phone num
    results = re.search(pattern, text)
    return results

class FindphoneSpider(scrapy.Spider):
    name = 'findphone'

    def __init__(self, DATA_FILE_IN, **kwargs):
        self.towns = read_in_data(DATA_FILE_IN)
        self.start_urls = [list(town.values())[-1] for town in self.towns] # Last index is town website
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        # Print Headers
        self.headers = list(self.towns[0].keys())
        self.headers.append('Town Clerk Phone')
        FEED_EXPORT_FIELDS = self.headers
        print(','.join(self.headers))
        super().__init__(**kwargs)  # python

    def start_requests(self):
        # Attach and index to the requests
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'index': index})

    def parse(self, response):
        # TODO Check status code
        
        # Get html Using lxml parser 
        html = BeautifulSoup(response.text, 'lxml')
        
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
       
        # Remove elements that aren't displayed
        for element in html.select('[style="display:none"]'):
            element.decompose()
        for element in html.select('[style="visibility:hidden"]'):
            element.decompose()

        # Clean up remaining text and look for phone numbers
        # Phone numbers will be in string format number;number
        text = html.find_all(text=True, recursive=True)
        lines = []
        for t in text:
            line = filter_text(t)
            if not line is None:
                lines.append(line.string[line.start(0):line.end(0)])
        phone = ';'.join(lines)

        # Correspond information with town
        index = response.meta['index']
        values = list(self.towns[index].values())
        values.append(phone)
        print(','.join(values))
        yield dict(zip(self.headers, values))

