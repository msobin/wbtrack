import json
import re
from urllib import parse

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from app.common.models import User, UserProduct, Product
from app.common.session import session
from app.wbbot.misc.product_card import get_product_card, get_product_markup
import app.wbbot.misc.env as env


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
        update.message.reply_html(get_product_card(product), reply_markup=get_product_markup(product))


def command_add_product(update, context):
    user = User.get_user(update.message.from_user.id, session)
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

    if session.query(UserProduct).filter_by(user_id=user.id).count() >= env.MAX_PRODUCT_COUNT:
        return update.message.reply_text(
            f'Вы отслеживаете максимально допустимое количество товаров: {env.MAX_PRODUCT_COUNT})')

    session.add(UserProduct(user_id=user.id, product_id=product.id))
    product.ref_count += 1
    session.commit()

    return update.message.reply_html(f'✅ Товар <a href="{code}">{product.url}</a> добавлен в список')


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
