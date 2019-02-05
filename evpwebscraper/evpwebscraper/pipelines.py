# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from bs4 import BeautifulSoup
import re

from . conf import *
from . helper_functions import *

class EvpwebscraperPipeline(object):
    keys = [
        #re.compile("phone"),
        re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}") # Regex for phone num
    ]
    def process_item(self, item, spider):
        html = BeautifulSoup(item['raw_html'], 'lxml')
        # Remove javascript and stylesheets
        for script in html(["script", "style"]):
            script.decompose()
        # Clean up remaining text and look for phone numbers
        # Phone numbers will be in string format number;number
        lines = [line.lower() for line in html.stripped_strings if any(key.match(line.lower()) for key in self.keys)]
        phone = ';'.join(lines)
        return item

