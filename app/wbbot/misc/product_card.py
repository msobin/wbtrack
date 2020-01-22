import json

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from app.common.models import ProductPrice


def get_product_card(product):
    card = f'🛍️ {product.name_f}\n\n'
    card += f'<b>{format_product_price(product)}</b>'
    return card


def get_product_markup(product):
    delete_button = InlineKeyboardButton(
        '❌ Удалить',
        callback_data=json.dumps({'action': 'delete_product', 'product_id': str(product.id)})
    )
    price_button = InlineKeyboardButton(
        '📈 Цены',
        callback_data=json.dumps({'action': 'prices_history', 'product_id': str(product.id)})
    )

    return InlineKeyboardMarkup([[delete_button, price_button]])


def format_product_price(product):
    if not product.current_price or product.current_price.value is None:
        return '💰 нет данных'

    price_icon = get_price_icon(product.current_price_value, product.previous_price_value)
    price_value = ProductPrice.format_price_value(product.current_price_value, product.domain)

    return f'{price_icon} {price_value}'


def get_price_icon(current_value, prev_value):
    price_icon = '💰'

    if prev_value and current_value:
        if current_value < prev_value:
            price_icon = '🔻'
        if current_value > prev_value:
            price_icon = '🔺'

    return price_icon
