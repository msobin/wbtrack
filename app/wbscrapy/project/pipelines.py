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
        product = spider.products[int(item['code'])]

        picker = list(map(lambda code: int(code), item.get('picker', [])))
        picker = list(filter(lambda code: code != product.code, picker))

        for code in picker:
            if not spider.session.query(Product).filter_by(code=code).first():
                spider.session.add(
                    Product(code=code, domain=product.domain, status=Product.STATUS_NEW))

        product.status = Product.STATUS_REGULAR
        product.name = item.get('name')
        # product.brand = item.get('brand')
        product.brand_id = self.get_brand_id(spider, item.get('brand'))
        product.images = item.get('images', [])
        product.picker = picker
        product.size_list = item.get('size_list')
        product.updated_at = datetime.datetime.now()
        product.catalog_category_ids = PostgresPipeline.process_categories(spider.session, item.get(
            'categories')) if item.get('categories') else []

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
    def process_categories(session, categories):
        categories_dict = {v['hash']: v['category'] for v in categories}

        hashes = list(map(lambda v: v['hash'], categories))
        db_hashes = [v.hash for v in session.query(CatalogCategory.hash).filter(CatalogCategory.hash.in_(hashes)).all()]
        diff_hashes = list(set(hashes) - set(db_hashes))

        for key in diff_hashes:
            session.add(CatalogCategory(hash=key, title=categories_dict[key]))

        db_hash_ids = {v.hash: v.id for v in
                       session.query(CatalogCategory).filter(CatalogCategory.hash.in_(hashes)).all()}

        ids = []
        for category in categories:
            ids.append(db_hash_ids[category['hash']])

        return ids

    @staticmethod
    def get_brand_id(spider, title):
        if title in spider.brands:
            return spider.brands[title].id

        brand = Brand(title=title)

        spider.session.add(brand)
        spider.session.commit()

        spider.brands[title] = brand

        return brand.id
