# -*- coding: utf-8 -*-
import scrapy
import re
from string import printable
from bs4 import BeautifulSoup

from .. conf import *

def filter_element(element):
    formated_element = ''
    try:
        formated_element = re.sub('([\n\t,]|\[\d\])*', '', element.get_text().strip())
    except IndexError: 
        formated_element = re.sub('([\n\t,]|\[\d\])*', '', element.find('a').get_text().strip())
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
        # Get table rows
        rows = table.find_all('tr')
        # Get table headers
        pattern = re.compile('t(d|h)')
        ths = rows[0].find_all(pattern)
        headers = []
        for th in ths:
            headers.append(filter_element(th))
            if th.get('colspan') and int(th.get('colspan')) > 1:
                for i in range(int(th.get('colspan')) - 1): 
                    # Will add spacing
                    # If colspan is 2, range(2 - 1) = range(1) = [0], so '-' will be appended one time 
                    headers.append('-') # Place holder
        FEED_EXPORT_FIELDS = headers
        print(','.join(headers))
        # Get table data
        for row in rows[1:]:
            elements = row.find_all(pattern)
            if len(elements) == 0:
                # If there are no elements
                continue
            filtered_elements = []
            for e in elements:
                filtered_elements.append(filter_element(e))
                if e.get('colspan') and int(e.get('colspan')) > 1:
                    for i in range(int(e.get('colspan')) - 1): 
                        # Will add spacing
                        # If colspan is 2, range(2 - 1) = range(1) = [0], so '-' will be appended one time 
                        filtered_elements.append('-') # Place holder
            if len(filtered_elements) != len(headers):
                # Skip line if length is incorrect since this will mess up output
                continue
            print(','.join(filtered_elements))
            yield dict(zip(headers, filtered_elements)) 

