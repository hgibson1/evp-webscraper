# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .. helper_functions import *
from .. conf import *

def link_filter(href): 
    # Will grab all external links excluding search/google links
    pattern = re.compile('^(http|https)://[.0-9a-z-_/?=]*$')
    return href is not None and not 'google' in href.lower() and re.match(pattern, href.lower())

class GooglesearchSpider(scrapy.Spider):
    name = 'googlesearch'
    allowed_domains = ['www.google.com']

    def __init__(self, DATA_FILE_IN, column=COLUMN, state=STATE, search_for=SEARCH_FOR, **kwargs):
        # Read in town
        self.column = column
        self.search_for = search_for
        self.towns = read_in_data(DATA_FILE_IN)
        # Start url is google search url for MA
        self.start_urls = ['https://www.google.com/search?q={}-clerk-{}-{}&start=0'.format(
            self.search_for,
            list(town.values())[self.column].lower().replace(' ',''), 
            state) for town in self.towns
        ]
        # Print headers
        self.headers = list(self.towns[0].keys())
        self.headers.append('{} Clerk Website'.format(self.search_for[0].upper() + self.search_for[1:]))
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
        county = ''
        town = ''
        pattern = ''
        website = ''
        if self.search_for is 'county':
        # If we're looking for a county
            county = list(self.towns[index].values())[self.column].lower().replace(' ', '')
            pattern = re.compile(
                '^(http|https)://[\.0-9a-z\-_]*{}[\.0-9a-z\-_]*/[\.0-9a-z\-_/?=]*'.format(county)
            )
        else:
            for header in self.headers:
            # Find county if the information is given
                if header.lower() == 'county':
                    county = self.towns[index][header].lower().replace(' ', '')        
            town = list(self.towns[index].values())[self.column].lower().replace(' ', '')
            # Similar to link filter except searches for town name in domain
            pattern = re.compile(
                '^(http|https)://[\.0-9a-z\-_]*{}[\.0-9a-z\-_]*/[\.0-9a-z\-_/?=]*'.format(town)
            )
        # Find first link with town name in domain and 'clerk' in url
        for link in website_links:
            if self.search_for == 'county' and re.match(pattern, link.lower()) and 'clerk' in link.lower():
                website = link
                break
            elif self.search_for != 'county' and county != '' and not county in link.lower() and not 'county' in link.lower() and re.match(pattern, link.lower()) and 'clerk' in link.lower():
                website = link
                break
            elif self.search_for != 'county' and county == '' and re.match(pattern, link.lower()) and 'clerk' in link.lower():
                website = link
                break
        # Otherwise find first link with town name in domain 
        if website is '':
            for link in website_links:
                if self.search_for == 'county' and re.match(pattern, link.lower()):
                    website = link
                    break
                elif self.search_for != 'county' and county != '' and not county in link.lower() and not 'county' in link.lower() and re.match(pattern, link.lower()):
                    website = link
                    break
                elif self.search_for != 'county' and county == '' and re.match(pattern, link.lower()):
                    website = link
                    break
        # Otherwise find first link containing name of the town/county
        if website is '':
            for link in website_links:
                if self.search_for == 'county' and county in link.lower():
                    website = link
                    break
                elif self.search_for != 'county' and county != '' and town in link.lower() and not county in link.lower() and not 'county' in link.lower():
                    website = link
                    break
                elif self.search_for != 'county' and county == '' and town in link.lower():
                    website = link
                    break
                elif self.search_for != 'county' and county != '' and 'clerk' in link.lower() and not county in link.lower() and not 'county' in link.lower():
                    website = link
                    break
        # Otherwise find first link containing the word 'clerk'
        if website is '':
            for link in website_links:
                if 'clerk' in link.lower():
                    website = link
                    break
        # Otherwise find first link on page
        if website is '':
            website = website_links[0]
        
        values = list(self.towns[index].values())
        values.append(website)
        print(','.join(values))
        yield dict(zip(self.headers, values))

