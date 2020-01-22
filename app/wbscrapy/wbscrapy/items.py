# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, Identity


def get_price(value):
    if len(value) == 0:
        return [0]

    return int(''.join(filter(lambda c: c.isdigit(), value[0])))


def get_images(value):
    return list(map(lambda href: 'https:' + href, value))


class Product(scrapy.Item):
    product_model = scrapy.Field(output_processor=TakeFirst())
    picker = scrapy.Field(output_processor=Identity())
    brand = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field(input_processor=get_images)
    price = scrapy.Field(input_processor=get_price, output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())

