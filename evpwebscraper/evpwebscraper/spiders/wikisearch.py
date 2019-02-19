# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from .. conf import *

def element_filter(element):
    formated_element = ''
    try:
        formated_element = element.get_text().split('[')[0].strip().replace(',', '')
    except IndexError: 
        formated_element = element.find('a').find('title').get_text().split(',')[0].strip().replace(',', '')
    return formated_element

class WikisearchSpider(scrapy.Spider):
    name = 'wikisearch'
    allowed_domains = ['en.wikipedia.org']

    def __init__(self, wiki_link=WIKI_LINK, **kwargs):
        # Use wiki link in conf.py or passed as command line argument
        self.start_urls = [wiki_link]
        super().__init__(**kwargs)

    def parse(self, response):
        # Get HTML
        html = BeautifulSoup(response.text, 'lxml')
    
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        
        # Get table of municipalities
        table = html.find('table')

        # Get table headers
        headers = [th.get_text().split('[')[0].strip() for th in table.find_all('th')]
        FEED_EXPORT_FIELDS = headers

        # Get table rows
        rows = table.find_all('tr')
        for row in rows:
            elements = row.find_all('td')
            if len(elements) == 0:
                continue
            filtered_elements = [element_filter(e) for e in elements]
            yield dict(zip(headers, filtered_elements)) 

