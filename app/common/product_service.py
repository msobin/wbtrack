from common.models import *


class ProductService:
    def __init__(self, db):
        self.session = db.get_session()

    def get_product_by_id(self, product_id):
        return self.session.query(Product).filter_by(id=product_id).first()

    def get_product_by_code(self, domain, code):
        product = self.session.query(Product).filter_by(domain=domain, code=code).first()

        if not product:
            self.create_product(domain, code)

            return self.get_product_by_code(domain, code)

        return product

    def get_user_product(self, user_id, product_id):
        return self.session.query(UserProduct).filter_by(user_id=user_id, product_id=product_id).first()

    def create_product(self, domain, code):
        self.session.add(Product(domain=domain, code=code, status=Product.STATUS_NEW))
        self.session.commit()

    def add_user_product(self, user_id, product_id):
        self.session.add(
            UserProduct(user_id=user_id, product_id=product_id, settings=UserProductSettings(),
                        price=UserProductPrice()))

        self.session.query().filter(Product.id == product_id).update({'ref_count': (Product.ref_count + 1)})
        self.session.commit()

    def delete_user_product(self, user_id, product_id):
        user_product = self.session.query(UserProduct).filter_by(user_id=user_id,
                                                                 product_id=product_id).first()

        self.session.query(UserProductSettings).filter_by(user_product_id=user_product.id).delete()
        self.session.query(UserProduct).filter_by(user_id=user_id, product_id=product_id).delete()
        self.session.query(UserProductPrice).filter_by(user_id=user_id, product_id=product_id).delete()
        self.session.query().filter(Product.id == product_id).update({'ref_count': (Product.ref_count - 1)})

        self.session.commit()

    def is_user_product_exist(self, user_id, product_id):
        q = self.session.query(UserProduct).filter_by(user_id=user_id, product_id=product_id)

        return self.session.query(q.exists())

    def get_user_product_count(self, user_id):
        return self.session.query(UserProduct).filter_by(user_id=user_id).count()
