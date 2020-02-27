from sqlalchemy import and_

from common.models import *


class PostgresPipeline(object):
    def __init__(self):
        pass

    def close_spider(self, spider):
        pass

    @staticmethod
    def process_item(product, spider):
        model = product['product_model']
        del product['product_model']

        picker = list(map(lambda code: int(code), product.get('picker', [])))
        picker = list(filter(lambda code: code != model.code, picker))

        for code in picker:
            if not spider.session.query(Product).filter_by(code=code).first():
                spider.session.add(
                    Product(code=code, domain=model.domain, status=Product.STATUS_NEW))

        model.status = Product.STATUS_REGULAR
        model.name = product.get('name')
        model.brand = product.get('brand')
        model.images = product.get('images', [])
        model.picker = picker
        model.size_list = product.get('size_list')
        model.updated_at = datetime.datetime.now()
        model.catalog_category_ids = PostgresPipeline.process_categories(spider.session, product.get(
            'categories')) if product.get('categories') else []

        model_price = model.price.value if model.price else None
        new_price = product.get('price')

        if model_price != new_price:
            spider.session.add(
                ProductPrice(product_id=model.id, value=new_price, prev_value=model_price))

        if new_price:
            spider.session.query(UserProductPrice).filter(and_(UserProductPrice.product_id == model.id,
                                                               UserProductPrice.price_start == None,
                                                               UserProductPrice.status == None)).update(
                {'price_start': new_price, 'price_end': new_price, 'status': UserProductPrice.STATUS_PROCESSED},
                synchronize_session=False)

            spider.session.query(UserProductPrice).filter(and_(UserProductPrice.product_id == model.id,
                                                               UserProductPrice.price_start != None,
                                                               UserProductPrice.price_end != new_price)).update(
                {'price_end': new_price, 'status': UserProductPrice.STATUS_UPDATED},
                synchronize_session=False)

            spider.session.commit()

        return product

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
