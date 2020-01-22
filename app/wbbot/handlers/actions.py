import json

from app.common.models import User, Product, ProductPrice, UserProduct
from app.common.session import session
from app.wbbot.misc.product_card import get_product_card, get_price_icon, get_product_markup


def inline_callback(update, context):
    callback_data = json.loads(update.callback_query.data)
    globals()['action_' + callback_data['action']](update.callback_query, callback_data)


def action_delete_product(query, data):
    user = User.get_user(query.from_user.id, session)

    product = session.query(Product).filter_by(id=data['product_id']).first()
    user_product = session.query(UserProduct).filter_by(user_id=user.id,
                                                        product_id=data['product_id']).first()

    if user_product:
        session.query(UserProduct).filter_by(user_id=user.id, product_id=data['product_id']).delete()
        product.ref_count -= 1
        session.commit()
    else:
        return query.message.reply_text('❗ Товар не найден')

    return query.message.reply_html(f'❌ Товар {product.name_f} удален из списка')


def action_prices_history(query, data):
    product = session.query(Product).filter_by(id=data['product_id']).first()
    product_prices = product.prices[:10]

    text = f'📈 Цены на {product.name_f}\n\n'

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

    return query.message.reply_html(text, reply_markup=get_product_markup(product))


def action_brand_list(query, data):
    brand = data['brand']
    user = User.get_user(query.from_user.id, session)

    for user_product in user.user_products:
        if user_product.product.brand == brand:
            query.message.reply_html(get_product_card(user_product.product),
                                     reply_markup=get_product_markup(user_product.product))
