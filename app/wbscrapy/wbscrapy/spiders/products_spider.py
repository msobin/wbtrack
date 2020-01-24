import scrapy
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from wbscrapy.items import Product

import common.models as models
from common.models import CatalogCategory
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

        catalog_categories = {}
        for product in self.session.query(models.Product).filter_by(status=status).all():
            yield scrapy.Request(url=product.url, callback=self.parse,
                                 cb_kwargs={'product_model': product, 'catalog_categories': catalog_categories})

        categories = session.query(CatalogCategory).filter(
            CatalogCategory.name.in_(list(catalog_categories.keys()))).all()

        diff_keys = list(set(catalog_categories.keys()) - set(list(map(lambda cc: cc.name, categories))))

        for key in diff_keys:
            self.session.add(CatalogCategory(name=key, title=catalog_categories[key]))

        self.session.commit()

    def parse(self, response, **kwargs):
        product_model = kwargs.get('product_model')
        catalog_categories = kwargs.get('catalog_categories')

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

        breadcrumbs = response.selector.xpath('//ul[@class="bread-crumbs"]/li/a').extract()

        for item in breadcrumbs[1:-1]:
            selector = Selector(text=item)
            category = selector.xpath('//a/@href').extract_first().split('/')[-1]
            title = selector.xpath('//a/span/text()').extract_first()
            catalog_categories[category] = title

        return loader.load_item()
