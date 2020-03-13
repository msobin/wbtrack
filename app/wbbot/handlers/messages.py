import json
import re
from urllib import parse

import pika
from sqlalchemy import or_, and_

import common.rmq as rmq
import wbbot.handlers.menu as menu
from common.di_container import user_service
from common.models import *
from common.session import session
from wbbot.misc.product_card import get_product_card, get_product_markup


def message_add_product(update, context):
    user = user_service.get_user(update.message.from_user.id)
    matches = re.findall(env.PRODUCT_REGEXP, update.message.text)

    if matches:
        parsed_uri = parse.urlparse(matches[0])
    else:
        return

    domain = parsed_uri.netloc.split('.')[-1]
    code = int("".join(filter(lambda c: c.isdigit(), parsed_uri.path)))

    product = Product.get_product(domain, code, session)
    user_product = session.query(UserProduct).filter_by(user_id=user.id, product_id=product.id).first()

    if user_product:
        return update.message.reply_text('Вы уже отслеживаете этот товар')

    if session.query(UserProduct).filter_by(user_id=user.id).count() >= user.max_product_count:
        return update.message.reply_text(
            f'Вы отслеживаете максимально допустимое количество товаров: {user.max_product_count})')

    session.add(
        UserProduct(user_id=user.id, product_id=product.id, settings=UserProductSettings(), price=UserProductPrice()))

    product.ref_count += 1
    session.commit()

    # todo move to rmq. make class that returns channel
    connection = pika.BlockingConnection(rmq.get_url_parameters())
    channel = connection.channel()

    channel.basic_publish(exchange=env.RMQ_EXCHANGE, routing_key=env.RMQ_QUEUE_NEW_PRODUCT,
                          body=json.dumps({'user_id': user.id, 'product_id': product.id}),
                          properties=pika.BasicProperties(delivery_mode=2))

    return update.message.reply_html(
        f'✅ Товар <a href="{code}">{product.url}</a> добавлен в список.')


def message_any(update, context):
    if context.user_data.get('action') == 'search':
        context.user_data['action'] = None
        user = user_service.get_user(update.message.from_user.id)

        products_ids = session.query(UserProduct.product_id).filter_by(user_id=user.id).distinct()

        q = '%' + update.message.text + '%'
        products = session.query(Product) \
            .filter(and_(or_(Product.name.ilike(q), Brand.title.ilike(q)), Product.id.in_(products_ids))) \
            .join(Brand, Product.brand_id == Brand.id) \
            .all()

        if not products:
            update.message.reply_text('Совпадений не найдено')

        for product in products:
            update.message.reply_html(get_product_card(product), reply_markup=get_product_markup(user.id, product))
    else:
        return menu.menu_item_select(update, context)
