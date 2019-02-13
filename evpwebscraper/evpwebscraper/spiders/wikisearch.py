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
    start_urls = [WIKI_LINK]

    def parse(self, response):
        # Get HTML
        html = BeautifulSoup(response.text, 'lxml')
    
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        
        # Get table of municipalities
        table = html.find('table')

        # Get table headers
        headers = table.find_all('th')
        header_string = headers[0].get_text().split('[')[0].strip()
        for header in headers[1:]:
            header_string = header_string + ',{}'.format(header.get_text().split('[')[0].strip())
        print(header_string)

        # Get table rows
        rows = table.find_all('tr')
        for row in rows:
            elements = row.find_all('td')
            if len(elements) == 0:
                continue
            row_string = element_filter(elements[0])
            for element in elements[1:]:
                row_string = row_string + ',{}'.format(element_filter(element))
            print(row_string)
