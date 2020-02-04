import json

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from common.models import User
from common.session import session
from wbbot.misc.product_card import get_product_card, get_product_markup
from common.models import Product, UserProduct
from sqlalchemy import func
from wbbot.misc.catalog import get_catalog, get_catalog_markup, get_count_wo_category


def command_start(update, context):
    update.message.reply_text(
        'Отправьте боту ссылку на товар, чтобы начать отслеживание цен\n\n'
        '/help - справка\n'
        '/list - список товаров\n'
        '/search - поиск товара\n'
        '/brands - список брендов\n',
        '/catalog - каталог товаров\n'
    )


def command_list(update, context):
    user = User.get_user(update.message.from_user.id, session)

    if not user.user_products:
        update.message.reply_text('Список товаров пуст')

    for user_product in user.user_products:
        product = user_product.product
        update.message.reply_html(get_product_card(product), reply_markup=get_product_markup(user.id, product))


def command_search(update, context):
    update.message.reply_text('Введите часть названия товара или бренда',
                              reply_markup=ForceReply())


def command_brands(update, context):
    user = User.get_user(update.message.from_user.id, session)
    user_product_ids = session.query(UserProduct.product_id).filter_by(user_id=user.id).distinct()
    group = session.query(Product.brand, func.count(Product.brand)).filter(Product.id.in_(user_product_ids)).group_by(
        Product.brand).all()

    buttons = []
    for brand, count in group:
        buttons.append([InlineKeyboardButton(
            f'{brand}: {count}',
            callback_data=json.dumps({'action': 'brand_list', 'brand': brand})
        )])

    return update.message.reply_html('👓 Бренды:', reply_markup=InlineKeyboardMarkup(buttons))


def command_catalog(update, context):
    user = User.get_user(update.message.from_user.id, session)
    rows = get_catalog(session, user.id, 1)
    wo_category_count = get_count_wo_category(session, user.id)

    if len(rows) == 0 and wo_category_count == 0:
        return update.message.reply_html('Нет данных')

    if wo_category_count != 0:
        rows.append((None, wo_category_count, 'Прочие'))

    return update.message.reply_html('🗂️ Категории:', reply_markup=get_catalog_markup(rows))


def command_ping(update, context):
    update.message.reply_text('pong')
