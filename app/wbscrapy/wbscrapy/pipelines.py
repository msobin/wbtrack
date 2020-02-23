from common.models import *


class PostgresPipeline(object):
    def __init__(self):
        pass

    def close_spider(self, spider):
        pass

    @staticmethod
    def process_item(product, spider):
        product_model = product['product_model']
        del product['product_model']

        picker = list(map(lambda code: int(code), product.get('picker', [])))
        picker = list(filter(lambda code: code != product_model.code, picker))

        for code in picker:
            if not spider.session.query(Product).filter_by(code=code).first():
                spider.session.add(
                    Product(code=code, domain=product_model.domain, status=Product.STATUS_NEW))

        product_model.status = Product.STATUS_REGULAR
        product_model.name = product.get('name')
        product_model.brand = product.get('brand')
        product_model.images = product.get('images', [])
        product_model.picker = picker
        product_model.size_list = product.get('size_list')
        product_model.updated_at = datetime.datetime.now()
        product_model.catalog_category_ids = PostgresPipeline.process_categories(spider.session, product.get(
            'categories')) if product.get('categories') else []

        price_value = product_model.price.value if product_model.price else None

        if price_value != product.get('price'):
            spider.session.add(
                ProductPrice(product_id=product_model.id, value=product.get('price'), prev_value=price_value))

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
