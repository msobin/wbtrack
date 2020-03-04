import scrapy
from scrapy.loader import ItemLoader

from wbscrapy.project.items import ProductItem
from common.models import *
from sqlalchemy import func


class ProductsSpider(scrapy.Spider):
    name = "products"

    def __init__(self, products, session, **kwargs):
        super().__init__(**kwargs)

        self.start_urls = [product.url for product in products]
        self.session = session
        self.products = {product.code: product for product in products}

        brands = self.session.query(Brand).filter(Brand.id.in_([product.brand_id for product in products])).all()
        self.brands = {brand.title: brand for brand in brands}

        catalog_categories_ids = self.session.query(func.unnest(Product.catalog_category_ids)) \
            .filter(Product.id.in_([product.id for product in products])).distinct()
        catalog_categories = self.session.query(CatalogCategory)\
            .filter(CatalogCategory.id.in_(catalog_categories_ids)).all()

        self.catalog_categories = {catalog_category.title: catalog_category for catalog_category in catalog_categories}

    def parse(self, response, **kwargs):
        loader = ItemLoader(item=ProductItem(), response=response)

        loader.add_xpath('code', '//span[@class="j-article"]/text()')
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
