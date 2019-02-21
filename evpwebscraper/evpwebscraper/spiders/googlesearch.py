# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .. helper_functions import *
from .. conf import *

def link_filter(href): 
    # Will grab all external links excluding search/google links
    pattern = re.compile('^(http|https)://[\.0-9a-z\-_/?=]*$')
    return href is not None and not 'google' in href.lower() and re.match(pattern, href.lower())

class GooglesearchSpider(scrapy.Spider):
    name = 'googlesearch'
    allowed_domains = ['www.google.com']

    def __init__(self, DATA_FILE_IN, town_column=TOWN_COLUMN, state=STATE, **kwargs):
        # Read in towns
        self.towns = read_in_data(DATA_FILE_IN)
        # Start url is google search url for MA
        self.start_urls = ['https://www.google.com/search?q=town-clerk-{}-{}&start=0'.format(
            list(town.values())[town_column].lower().replace(' ',''), 
            state) for town in self.towns
        ]
        # Print headers
        self.headers = list(self.towns[0].keys())
        self.headers.append('Town Clerk Website')
        FEED_EXPORT_FIELDS = self.headers
        print(','.join(self.headers))
        super().__init__(**kwargs)

    def start_requests(self):
        # Attach and index to the requests
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'index': index})

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

        # Find links to town clerk websites
        website_links = [a['href'] for a in html.find_all('a', href=link_filter)]
        
        # Find correct link and map to a town
        index = response.meta['index'] 
        # Similar to link filter except searches for town name in domain
        town = list(self.towns[index].values())[0].lower().replace(' ', '')
        pattern = re.compile(
            '^(http|https)://[\.0-9a-z\-_]*{}[\.0-9a-z\-_]*/[\.0-9a-z\-_/?=]*'.format(town)
        )
        website = ''
        # Find first link with town name in domain and 'clerk' in url
        for link in website_links:
            if re.match(pattern, link.lower()) and 'clerk' in link.lower():
                website = link
                break
        # Otherwise find first link with town name in domain 
        if website is '':
            for link in website_links:
                if re.match(pattern, link.lower()):
                    website = link
                    break
        # Otherwise find first link containing 'clerk' or the name of the town
        if website is '':
            for link in website_links:
                if town in link.lower() or 'clerk' in link.lower():
                    website = link
                    break
        # Otherwise find first link on page
        if website is '':
            website = website_links[0]
        values = list(self.towns[index].values())
        values.append(website)
        print(','.join(values))
        yield dict(zip(self.headers, values))

