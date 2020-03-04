import json

from sqlalchemy import func
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from common.models import *
from common.session import session
from wbbot.misc.catalog import get_catalog, get_catalog_markup, get_count_wo_category
from wbbot.misc.product_card import get_product_card, get_product_markup
from wbbot.misc.user import get_user


def products_list_all(update, context):
    user = get_user(update.message.from_user.id, session)

    product_ids = session.query(UserProduct.product_id).filter_by(user_id=user.id).distinct()
    products = session.query(Product).filter(Product.id.in_(product_ids)).distinct()

    return products_list(update, context, user, products)


def products_search(update, context):
    context.user_data['action'] = 'search'
    update.message.reply_text('Введите часть названия товара или бренда')


def brands_list(update, context):
    user = get_user(update.message.from_user.id, session)
    user_product_ids = session.query(UserProduct.product_id).filter_by(user_id=user.id).distinct()

    group = session.query(Brand.title, Brand.id, func.count(Product.brand_id)) \
        .join(Product, Product.brand_id == Brand.id) \
        .filter(Product.id.in_(user_product_ids)) \
        .group_by(Brand.title, Brand.id, Product.brand_id) \
        .order_by(Brand.title.asc())

    buttons = []
    for brand_title, brand_id, count in group:
        buttons.append([InlineKeyboardButton(
            f'{brand_title}: {count}',
            callback_data=json.dumps({'action': 'brand_list', 'brand_id': brand_id})
        )])

    update.message.reply_html('👓 Бренды:', reply_markup=InlineKeyboardMarkup(buttons))


def products_catalog(update, context):
    user = get_user(update.message.from_user.id, session)
    rows = get_catalog(session, user.id, 1)
    wo_category_count = get_count_wo_category(session, user.id)

    if len(rows) == 0 and wo_category_count == 0:
        return update.message.reply_html('Нет данных')

    if wo_category_count != 0:
        rows.append((None, wo_category_count, 'Прочие'))

    update.message.reply_html('🗂️ Категории:', reply_markup=get_catalog_markup(rows))


def product_list_by_notify(update, context, is_notify):
    user = get_user(update.message.from_user.id, session)

    product_ids = session.query(UserProduct.product_id).filter_by(user_id=user.id).join(UserProduct.settings).filter(
        UserProductSettings.is_price_notify == is_notify).distinct()

    products = session.query(Product).filter(Product.id.in_(product_ids)).distinct()

    return products_list(update, context, user, products)


def logout(update, context):
    user = get_user(update.message.from_user.id, session)

    session.query(UserProduct).filter_by(user_id=user.id).delete()
    session.delete(user)
    session.commit()

    update.message.reply_html('👋 Все Ваши данные удалены, бот больше не будет Вас беспокоить')


def products_list(update, context, user, products):
    products = list(products)

    if not products:
        update.message.reply_text('Список пуст')

    for product in products:
        update.message.reply_html(get_product_card(product), reply_markup=get_product_markup(user.id, product))
