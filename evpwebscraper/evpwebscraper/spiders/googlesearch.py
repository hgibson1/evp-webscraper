# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .. helper_functions import *
from .. conf import *

def town_website_filter(href):
    #print(href)
    pattern = re.compile(
        '^(http|https)://www\.[^masstownclerks][0-9a-z\-_]*(\.org|\.gov|\.ma\.us)/[/\-_0-9a-z]*clerk($|/$|/index)'
    )
    return href != None and re.match(pattern, href.lower())

def search_page_filter(href):
    pattern = re.compile('^/search\?q=ma\+town\+clerks')
    return href != None and re.match(pattern, href.lower())
    

class GooglesearchSpider(scrapy.Spider):
    name = 'googlesearch'
    allowed_domains = ['/home/naved/Documents/evp-webscraper/evpwebscraper']
    # Start url is google search url for MA
    #start_urls = ['https://www.google.com/search?q=ma+town+clerks']
    start_urls = ['file:///home/naved/Documents/evp-webscraper/evpwebscraper/ma-town-clerks-Google-Search.html']
    towns = read_in_data(DATA_FILE_IN)

    def parse(self, response):
        html = BeautifulSoup(response.text, 'lxml')
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        # Find links to town clerk websites
        website_links = [a['href'] for a in html.find_all('a', href=town_website_filter)]
        #print(website_links)
        for link in website_links:
            for town in self.towns:
                if town[HEADERS['town']].lower() in link.lower():
                    print("{} {}".format(town[HEADERS['town']], link))
        # Find other pages of google search
        search_pages = [response.urljoin(a['href']) for a in html.find_all('a', href=search_page_filter)]
        for search_page in search_pages:
            print(search_page)
            #yield scrapy.Request(search_page)

