import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY, Boolean
from sqlalchemy import Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import common.env as env
from common.db import Db

db = Db()
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
    price = relationship('UserProductPrice', uselist=False)


class UserProductPrice(Base):
    __tablename__ = 'user_product_price'

    STATUS_NONE = None
    STATUS_APPEARED = 1
    STATUS_UPDATED = 2
    STATUS_PROCESSED = 100

    id = Column(Integer, primary_key=True)
    user_product_id = Column(Integer, ForeignKey('user_product.id', ondelete='CASCADE'), index=True)
    price_start = Column(Integer)
    price_end = Column(Integer)
    status = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    user_product = relationship('UserProduct')


class UserProductSettings(Base):
    __tablename__ = 'user_product_settings'

    id = Column(Integer, primary_key=True)
    user_product_id = Column(Integer, ForeignKey('user_product.id', ondelete='CASCADE'), index=True)
    is_price_notify = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    user_product = relationship('UserProduct', uselist=False)


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (Index('uix_product_domain_code', 'domain', 'code', unique=True),)

    STATUS_NEW = 1
    STATUS_SATELLITE = 2
    STATUS_REGULAR = 10

    id = Column(Integer, primary_key=True)
    domain = Column(String)
    code = Column(Integer)
    name = Column(String, index=True)
    brand_id = Column(Integer, ForeignKey('brand.id'), index=True)
    images = Column(ARRAY(String), default=[])
    picker = Column(ARRAY(Integer), default=[])
    ref_count = Column(Integer, default=0)
    status = Column(Integer, default=1, index=True)
    catalog_category_ids = Column(ARRAY(Integer), default=[])
    size_list = Column(ARRAY(String), default=[])
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    price = relationship('ProductPrice', order_by='desc(ProductPrice.id)', uselist=False)
    prices = relationship('ProductPrice', order_by='desc(ProductPrice.id)')
    brand = relationship('Brand')

    @property
    def header(self):
        brand = self.brand.title if self.brand else None

        return f'<a href="{self.url}">{brand} / {self.name}</a>'

    @property
    def url(self):
        return f'https://www.wildberries.{self.domain}/catalog/{self.code}/detail.aspx'


class ProductPrice(Base):
    __tablename__ = 'product_price'

    # todo выпилить
    STATUS_NEW = 1
    STATUS_PROCESSED = 2

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), index=True)
    value = Column(Integer, nullable=True)
    prev_value = Column(Integer, nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    product = relationship('Product')

    @staticmethod
    def format_price_value(value, domain):
        if not value:
            return 'нет в наличии'

        return '{0} {1}'.format('{:,}'.format(value).replace(',', ' '), ProductPrice.get_domain_currency(domain))

    @staticmethod
    def get_domain_currency(domain):
        return {'kz': 'тг.', 'ru': 'руб.'}.get(domain, '')


class CatalogCategory(Base):
    __tablename__ = 'catalog_category'
    __table_args__ = (Index('uix_catalog_category_title', 'title', unique=True),)

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class Brand(Base):
    __tablename__ = 'brand'
    __table_args__ = (Index('uix_brand_title', 'title', unique=True),)

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


Base.metadata.create_all(db.engine)
