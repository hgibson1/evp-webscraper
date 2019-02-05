# -*- coding: utf-8 -*-
import scrapy

from .. conf import *

class GooglesearchSpider(scrapy.Spider):
    name = 'googlesearch'
    allowed_domains = ['www.google.com']
    start_urls = ['http:///']

    def parse(self, response):
        pass
