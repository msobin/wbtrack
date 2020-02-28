import scrapy
from scrapy.loader import ItemLoader
from wbscrapy.items import Product

import common.models as models
from common.session import session


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

        # if self.type == 'new':
        #     while True:
        #         method, properties, body = rmq_channel.basic_get(env.QUEUE_NEW_PRODUCTS)
        #
        #         if body:
        #             rmq_channel.basic_ack(delivery_tag=method.delivery_tag)
        #
        #             data = json.loads(body)
        #             product = self.session.query(models.Product).filter_by(id=data['product_id']).first()
        #
        #             yield scrapy.Request(url=product.url, callback=self.parse, cb_kwargs={'product_model': product})
        #         else:
        #             await asyncio.sleep(5)

        batch_size = self.crawler.settings.get('CONCURRENT_REQUESTS') * 100
        offset = 0

        while True:
            products = self.session.query(models.Product).filter_by(status=status).limit(batch_size).offset(
                offset).all()

            if not products:
                break

            for product in products:
                yield scrapy.Request(url=product.url, callback=self.parse, cb_kwargs={'product_model': product})

            offset += batch_size

    def parse(self, response, **kwargs):
        product_model = kwargs.get('product_model')

        loader = ItemLoader(item=Product(), response=response)

        loader.add_value('product_model', product_model)
        loader.add_xpath('picker', '//div[contains(@class, "colorpicker")]/ul/li/@data-cod1s')
        loader.add_xpath('brand', '//span[@class="brand"]/text()')
        loader.add_xpath('name', '//span[@class="name"]/text()')
        loader.add_xpath('images',
                         '//div[contains(@class, "pv-carousel")]//a[contains(@class, "j-carousel-image")]/@href')
        loader.add_xpath('price', '//span[@class="final-cost"]/text()')
        loader.add_xpath('description', '//div[contains(@class, "description-text")]/p/text()')
        loader.add_xpath('categories', '//ul[@class="bread-crumbs"]/li/a')
        loader.add_xpath('size_list',
                         '//div[contains(@class, "size-list") and not(contains(@class, "hide"))]/label[not(contains(@class, "disabled"))]/@data-size-name')

        return loader.load_item()
