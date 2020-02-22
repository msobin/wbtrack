from telegram import ReplyKeyboardMarkup

import wbbot.actions.common as actions
from wbbot.handlers.menu import menu


def command_start(update, context):
    update.message.reply_html(
        'Отправьте боту ссылку на товар\n\n'
        '/help - справка\n'
        '/list - список товаров\n'
        '/search - поиск товара\n'
        '/brands - список брендов\n'
        '/catalog - каталог товаров\n'
        '/logout - выход\n',
        reply_markup=ReplyKeyboardMarkup([[key] for key in menu.keys()])
    )


def command_list(update, context):
    return actions.products_list(update, context)


def command_search(update, context):
    return actions.products_search(update, context)


def command_brands(update, context):
    return actions.brands_list(update, context)


def command_catalog(update, context):
    return actions.products_catalog(update, context)


def command_ping(update, context):
    update.message.reply_text('pong')


def command_logout(update, context):
    return actions.logout(update, context)
