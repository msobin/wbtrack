import scrapy
from scrapy.loader import ItemLoader
from wbscrapy.items import Product

import app.common.models as models
from app.common.session import session


class ProductsSpider(scrapy.Spider):
    name = "products"

    def __init__(self, type=''):
        scrapy.Spider.__init__(self)
        self.type = type

        self.session = session

    def close(self, spider, reason):
        pass

    def start_requests(self):
        if self.type == 'new':
            status = models.Product.STATUS_NEW
        else:
            status = models.Product.STATUS_REGULAR

        for product in self.session.query(models.Product).filter_by(status=status).all():
            yield scrapy.Request(url=product.url, callback=self.parse, cb_kwargs={'product_model': product})

    def parse(self, response, product_model):
        loader = ItemLoader(item=Product(), response=response)
        loader.add_value('product_model', product_model)
        loader.add_xpath('picker', '//div[contains(@class, "colorpicker")]/ul/li/@data-cod1s')
        loader.add_xpath('brand', '//span[@class="brand"]/text()')
        loader.add_xpath('name', '//span[@class="name"]/text()')
        loader.add_xpath('images',
                         '//div[contains(@class, "pv-carousel")]//a[contains(@class, "j-carousel-image")]/@href')
        loader.add_xpath('price', '//span[@class="final-cost"]/text()')
        loader.add_xpath('description', '//div[contains(@class, "description-text")]/p/text()')

        return loader.load_item()
