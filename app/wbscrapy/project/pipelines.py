from sqlalchemy import and_

from common.models import *


class PostgresPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        product = spider.products[item.get('url')]

        picker = list(map(lambda code: int(code), item.get('picker', [])))
        picker = list(filter(lambda code: code != product.code, picker))

        for code in picker:
            if not spider.session.query(Product).filter_by(code=code).first():
                spider.session.add(
                    Product(code=code, domain=product.domain, status=Product.STATUS_SATELLITE))

        product.status = Product.STATUS_REGULAR
        product.name = item.get('name')
        product.brand_id = self.get_brand_id(spider, item.get('brand'))
        product.images = item.get('images', [])
        product.picker = picker
        product.size_list = item.get('size_list')
        product.catalog_category_ids = self.get_catalog_category_ids(spider, item.get('categories'))

        product_price = product.price.value if product.price else None
        item_price = item.get('price')

        if product_price != item_price:
            spider.session.add(
                ProductPrice(product_id=product.id, value=item_price, prev_value=product_price))

        if item_price:
            user_product_ids = spider.session.query(UserProduct.id).filter_by(product_id=product.id).distinct()

            spider.session.query(UserProductPrice).filter(and_(UserProductPrice.user_product_id.in_(user_product_ids),
                                                               UserProductPrice.price_start == None,
                                                               UserProductPrice.status == None)).update(
                {'price_start': item_price, 'price_end': item_price, 'status': UserProductPrice.STATUS_APPEARED},
                synchronize_session=False)

            spider.session.query(UserProductPrice).filter(and_(UserProductPrice.user_product_id.in_(user_product_ids),
                                                               UserProductPrice.price_start != None,
                                                               UserProductPrice.price_end != item_price)).update(
                {'price_end': item_price, 'status': UserProductPrice.STATUS_UPDATED},
                synchronize_session=False)

        spider.session.commit()

        return item

    @staticmethod
    def get_brand_id(spider, title):
        # critical section ?
        if title in spider.brands:
            model = spider.brands[title]
        else:
            model = spider.session.query(Brand).filter_by(title=title).first()

            if not model:
                model = Brand(title=title)
                spider.session.add(model)
                spider.session.commit()

        spider.brands[title] = model

        return model.id

    @staticmethod
    def get_catalog_category_ids(spider, categories):
        # critical section ?
        category_ids = []

        if categories is None:
            return category_ids

        for category in categories:
            if category in spider.catalog_categories:
                model = spider.catalog_categories[category]
            else:
                model = spider.session.query(CatalogCategory).filter_by(title=category).first()

                if not model:
                    model = CatalogCategory(title=category)
                    spider.session.add(model)
                    spider.session.commit()

            spider.catalog_categories[category] = model
            category_ids.append(model.id)

        return category_ids
