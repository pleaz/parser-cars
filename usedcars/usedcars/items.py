# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UsedcarsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class DealerItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    cars = scrapy.Field()
