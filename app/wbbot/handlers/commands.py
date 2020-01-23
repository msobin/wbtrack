import json

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from app.common.models import User
from app.common.session import session
from app.wbbot.misc.product_card import get_product_card, get_product_markup


def command_start(update, context):
    update.message.reply_text(
        'Отправьте боту ссылку на товар, чтобы начать отслеживание цен\n\n'
        '/help - справка\n'
        '/ping - потыкать бота палочкой\n'
        '/list - список товаров\n'
        '/search - поиск товара\n'
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


def command_brand_list(update, context):
    user = User.get_user(update.message.from_user.id, session)

    if not user.user_products:
        update.message.reply_text('Список товаров пуст')

    brands = {}
    for user_product in user.user_products:
        brand = user_product.product.brand

        if brand in brands.keys():
            brands[user_product.product.brand] += 1
        else:
            brands[user_product.product.brand] = 1

    buttons = []
    for brand in sorted(brands):
        buttons.append([InlineKeyboardButton(
            f'{brand}: {brands[brand]}',
            callback_data=json.dumps({'action': 'brand_list', 'brand': brand})
        )])

    return update.message.reply_html('Брэнды:', reply_markup=InlineKeyboardMarkup(buttons))


def command_ping(update, context):
    update.message.reply_text('pong')
