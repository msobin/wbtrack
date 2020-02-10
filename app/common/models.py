import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY, Boolean
from sqlalchemy import Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import common.env as env
from common.session import engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, index=True)
    max_product_count = Column(Integer, default=env.MAX_PRODUCT_COUNT)
    created_at = Column(DateTime, default=datetime.datetime.now)
    user_products = relationship('UserProduct')


class UserProduct(Base):
    __tablename__ = 'user_product'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    product_id = Column(Integer, ForeignKey('product.id'), index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    product = relationship('Product')
    user = relationship('User')
    settings = relationship('UserProductSettings', uselist=False)


class UserProductSettings(Base):
    __tablename__ = 'user_product_settings'

    id = Column(Integer, primary_key=True)
    user_product_id = Column(Integer, ForeignKey('user_product.id'), index=True)
    is_price_notify = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    user_product = relationship('UserProduct', uselist=False)


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (Index('uix_product_domain_code', 'domain', 'code', unique=True),)

    STATUS_NEW = 1
    STATUS_REGULAR = 2

    id = Column(Integer, primary_key=True)
    domain = Column(String)
    code = Column(Integer)
    name = Column(String, index=True)
    brand = Column(String, index=True)
    images = Column(ARRAY(String), default=[])
    picker = Column(ARRAY(Integer), default=[])
    ref_count = Column(Integer, default=0)
    status = Column(Integer, default=1, index=True)
    catalog_category_ids = Column(ARRAY(Integer), default=[])
    size_list = Column(ARRAY(String), default=[])
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    prices = relationship('ProductPrice', order_by='desc(ProductPrice.id)')

    @staticmethod
    def get_product(domain, code, session):
        product = session.query(Product).filter_by(domain=domain, code=code).first()

        if not product:
            session.add(Product(domain=domain, code=code, status=Product.STATUS_NEW))
            session.commit()

            product = session.query(Product).filter_by(domain=domain, code=code).first()

        return product

    @property
    def current_price(self):
        try:
            return self.prices[0]
        except IndexError:
            return None

    @property
    def previous_price(self):
        try:
            return self.prices[1]
        except IndexError:
            return None

    @property
    def current_price_value(self):
        try:
            return self.current_price.value
        except AttributeError:
            return None

    @property
    def previous_price_value(self):
        try:
            return self.previous_price.value
        except AttributeError:
            return None

    @property
    def header(self):
        return f'<a href="{self.url}">{self.brand} / {self.name}</a>'

    @property
    def url(self):
        return f'https://www.wildberries.{self.domain}/catalog/{self.code}/detail.aspx'


class ProductPrice(Base):
    __tablename__ = 'product_price'

    STATUS_NEW = 1
    STATUS_PROCESSED = 2

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), index=True)
    value = Column(Integer, nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    product = relationship('Product')

    @staticmethod
    def format_price_value(value, domain):
        if not value:
            return 'нет в продаже'

        return '{0} {1}'.format('{:,}'.format(value).replace(',', ' '), ProductPrice.get_domain_currency(domain))

    @staticmethod
    def get_domain_currency(domain):
        return {'kz': 'тг.', 'ru': 'руб.'}.get(domain, '')


class CatalogCategory(Base):
    __tablename__ = 'catalog_category'
    __table_args__ = (Index('uix_catalog_category_hash', 'hash', unique=True),)

    id = Column(Integer, primary_key=True)
    hash = Column(String(32), index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


Base.metadata.create_all(engine)
