# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import hashlib

import scrapy
from scrapy.loader.processors import TakeFirst, Identity
from scrapy.selector import Selector


def get_price(value):
    if len(value) == 0:
        return [0]

    return int(''.join(filter(lambda c: c.isdigit(), value[0])))


def get_images(value):
    return list(map(lambda href: 'https:' + href, value))


def get_categories(breadcrumbs):
    categories = []

    for a in breadcrumbs[1:]:
        selector = Selector(text=a)
        categories.append(selector.xpath('//a/span/text()').extract_first())

    return categories


class ProductItem(scrapy.Item):
    url = scrapy.Field(output_processor=TakeFirst())
    code = scrapy.Field(output_processor=TakeFirst())
    picker = scrapy.Field(output_processor=Identity())
    brand = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field(input_processor=get_images)
    price = scrapy.Field(input_processor=get_price, output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())
    categories = scrapy.Field(input_processor=get_categories)
    size_list = scrapy.Field()
