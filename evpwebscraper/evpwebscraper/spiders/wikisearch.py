# -*- coding: utf-8 -*-
import scrapy
from string import printable
from bs4 import BeautifulSoup

from .. conf import *

def element_filter(element):
    formated_element = ''
    try:
        formated_element = element.get_text().split('[')[0].strip().replace(',', '')
    except IndexError: 
        formated_element = element.find('a').get_text().split('[')[0].strip().replace(',', '')
    return ''.join(formated_element)

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

        # Remove elements that aren't displayed
        for element in html.select('[style="display:none"]'):
            element.decompose()
        for element in html.select('[style="visibility:hidden"]'):
            element.decompose()
        
        # Get table of municipalities
        table = html.find('table', {"class": "wikitable sortable"})

        # Get table headers
        headers = [th.get_text().split('[')[0].strip() for th in table.find_all('th')]
        FEED_EXPORT_FIELDS = headers

        # Get table rows
        rows = table.find_all('tr')
        for row in rows[1:]:
            elements = row.find_all('th')
            elements.extend(row.find_all('td'))
            if len(elements) == 0:
                continue
            filtered_elements = [element_filter(e) for e in elements]
            yield dict(zip(headers, filtered_elements)) 

