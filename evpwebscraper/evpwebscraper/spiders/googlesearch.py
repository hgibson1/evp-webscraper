# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .. helper_functions import *
from .. conf import *


def town_website_filter(href):
    pattern = re.compile(
        '^(http|https)://[\.0-9a-z\-_]*(\.com|\.org|\.gov|\.us)/[/\-_0-9a-z]*clerk($|/$|/index)'
    )
    return href != None and re.match(pattern, href.lower())


class GooglesearchSpider(scrapy.Spider):
    name = 'googlesearch'
    allowed_domains = ['www.google.com']
    towns = read_in_data(DATA_FILE_IN)
    # Start url is google search url for MA
    start_urls = ['https://www.google.com/search?q=town-clerk-{}-{}&start=0'.format(
            list(town.values())[0].lower(), 
            STATE
        ) for town in towns
    ]

    def start_requests(self):
        # Print headers
        header_string = ','.join(list(self.towns[0].keys())) + ',Town Clerk Website'
        print(header_string)
        
        # Attach and index to the requests
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={'index': index})

    def parse(self, response):
        # Get HTML
        html = BeautifulSoup(response.text, 'lxml')
        
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        
        # Find links to town clerk websites
        website_links = [a['href'] for a in html.find_all('a', href=town_website_filter)]
        
        # Find correct link and map to a town
        index = response.meta['index'] 
        pattern = re.compile('^(http|https)://[\.0-9a-z\-_]*{}[\.0-9a-z\-_]*(\.com|\.org|\.gov|\.us)/'.format(
            list(self.towns[index].values())[0].lower()
            )
        )
        for link in website_links:
            if re.match(pattern, link.lower()):
                link_string = ','.join(list(self.towns[index].values())) + ',' + link
                print(link_string)
                break

