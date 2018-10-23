# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UsedcarItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CarItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    key = scrapy.Field()
    condition = scrapy.Field()
    make = scrapy.Field()
    model = scrapy.Field()
    year = scrapy.Field()
    mileage = scrapy.Field()
    variant = scrapy.Field()
    body = scrapy.Field()
    exterior_color = scrapy.Field()
    door = scrapy.Field()
    transmission = scrapy.Field()
    engine_size = scrapy.Field()
    fuel_type = scrapy.Field()
    co_emission = scrapy.Field()
    tax_cost = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    features = scrapy.Field()
    description = scrapy.Field()
