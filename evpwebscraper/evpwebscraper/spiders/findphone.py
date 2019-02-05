# -*- coding: utf-8 -*-
import scrapy
from . evpwebscraperbase import EvpwebscraperbaseSpider

class FindphoneSpider(EvpwebscraperbaseSpider):
    name = 'findphone'
    
    def parse(self, response):
        super().parse(response)
