import json

from sqlalchemy import func
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from common.models import Product, UserProduct
from common.session import session
from wbbot.misc.catalog import get_catalog, get_catalog_markup, get_count_wo_category
from wbbot.misc.product_card import get_product_card, get_product_markup
from wbbot.misc.user import get_user


def products_list(update, context):
    user = get_user(update.message.from_user.id, session)

    if not user.user_products:
        update.message.reply_text('Список товаров пуст')

    for user_product in user.user_products:
        product = user_product.product
        update.message.reply_html(get_product_card(product), reply_markup=get_product_markup(user.id, product))


def products_search(update, context):
    context.user_data['action'] = 'search'
    update.message.reply_text('Введите часть названия товара или бренда',
                              reply_markup=ForceReply())


def brands_list(update, context):
    user = get_user(update.message.from_user.id, session)
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


def products_catalog(update, context):
    user = get_user(update.message.from_user.id, session)
    rows = get_catalog(session, user.id, 1)
    wo_category_count = get_count_wo_category(session, user.id)

    if len(rows) == 0 and wo_category_count == 0:
        return update.message.reply_html('Нет данных')

    if wo_category_count != 0:
        rows.append((None, wo_category_count, 'Прочие'))

    return update.message.reply_html('🗂️ Категории:', reply_markup=get_catalog_markup(rows))


def logout(update, context):
    user = get_user(update.message.from_user.id, session)

    session.query(UserProduct).filter_by(user_id=user.id).delete()
    session.delete(user)
    session.commit()

    update.message.reply_html('👋 Все Ваши данные удалены, бот больше не будет Вас беспокоить')
