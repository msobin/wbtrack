import json

from wbbot.misc.catalog import get_catalog, get_catalog_markup
from common.models import User, Product, ProductPrice, UserProduct, UserProductSettings
from common.session import session
from wbbot.misc.product_card import get_product_card, get_price_icon, get_product_markup


def inline_callback(update, context):
    callback_data = json.loads(update.callback_query.data)
    globals()['action_' + callback_data['action']](update.callback_query, callback_data)


def action_delete_product(query, data):
    user = User.get_user(query.from_user.id, session)
    product_id = data['product_id']

    product = session.query(Product).filter_by(id=product_id).first()
    user_product = session.query(UserProduct).filter_by(user_id=user.id,
                                                        product_id=product_id).first()

    if user_product:
        session.query(UserProductSettings).filter_by(user_product_id=user_product.id).delete()
        session.query(UserProduct).filter_by(user_id=user.id, product_id=product_id).delete()
        product.ref_count -= 1
        session.commit()
    else:
        return query.message.reply_text('❗ Товар не найден')

    return query.message.reply_html(f'❌ Товар {product.header} удален из списка')


def action_prices_history(query, data):
    user = User.get_user(query.from_user.id, session)

    product = session.query(Product).filter_by(id=data['product_id']).first()
    product_prices = product.prices[:30]

    text = f'📈 Цены на {product.header}\n\n'

    if not product_prices:
        text += 'нет данных'

    for idx, product_price in enumerate(product_prices):
        current_value = product_price.value
        try:
            prev_value = product_prices[idx + 1].value
        except IndexError:
            prev_value = None

        price_icon = get_price_icon(current_value, prev_value)
        price_value = ProductPrice.format_price_value(current_value, product.domain)

        text += f'{product_price.created_at.date()}  {price_icon} {price_value}\n'

    return query.message.reply_html(text, reply_markup=get_product_markup(user.id, product))


def action_brand_list(query, data):
    brand = data['brand']
    user = User.get_user(query.from_user.id, session)

    for user_product in user.user_products:
        if user_product.product.brand == brand:
            query.message.reply_html(get_product_card(user_product.product),
                                     reply_markup=get_product_markup(user.id, user_product.product))


def action_price_notify(query, data):
    user = User.get_user(query.from_user.id, session)
    user_product = session.query(UserProduct).filter_by(user_id=user.id, product_id=data['product_id']).first()

    if not user_product:
        return

    user_product.settings.is_price_notify = not data['n']
    session.commit()

    if user_product.settings.is_price_notify:
        text = f'🔔 Включены уведомления для {user_product.product.header}'
    else:
        text = f'🔕 Отключены уведомления для {user_product.product.header}'

    return query.message.reply_html(text, reply_markup=get_product_markup(user.id, product=user_product.product))


def action_catalog_category(query, data):
    user = User.get_user(query.from_user.id, session)
    category_id = data['id']

    if category_id is None:
        product_ids = session.query(UserProduct.product_id).filter_by(user_id=user.id).distinct()
        products = session.query(Product).filter(Product.id.in_(product_ids),
                                                 Product.catalog_category_ids.is_(None))

        for product in products:
            query.message.reply_html(get_product_card(product),
                                     reply_markup=get_product_markup(user.id, product))

    else:
        rows = get_catalog(session, user.id, data['level'], category_id)

        if len(rows) < 2:
            product_ids = session.query(UserProduct.product_id).filter_by(user_id=user.id).distinct()
            products = session.query(Product).filter(Product.id.in_(product_ids),
                                                     Product.catalog_category_ids.any(category_id))
            for product in products:
                query.message.reply_html(get_product_card(product),
                                         reply_markup=get_product_markup(user.id, product))

        else:
            return query.message.reply_html('🗂️ Категории:', reply_markup=get_catalog_markup(rows))
