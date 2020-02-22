from telegram import ReplyKeyboardMarkup

import wbbot.actions.common as actions

MENU_ITEM_HOME = '🏠 Главное меню'
MENU_ITEM_BACK = '🔙 Назад'

menu = {
    '🛍️ Товары': {
        '🔍 Найти': 'action_search',
        '📃 Список': 'action_list',
        '🗂️ Каталог': 'action_catalog',
        '👓 Брэнды': 'action_brands',

    },
    '⚙️ Настройки': 'action_stub',
}


def menu_item_select(update, context):
    item = update.message.text
    path = context.user_data.get('menu_path')

    if item == MENU_ITEM_HOME:
        path = None
    elif item == MENU_ITEM_BACK:
        path = '.'.join(path.split('.')[:-1])
    else:
        path = '.'.join([path, item]) if path else item

    sub_menu = get_sub_menu(path)

    if type(sub_menu) is dict:
        reply_keyboard = get_reply_keyboard(path)
    else:
        return globals()[sub_menu](update, context)

    context.user_data['menu_path'] = path
    update.message.reply_text('test', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))


def get_reply_keyboard(path):
    sub_menu = get_sub_menu(path)

    reply_keyboard = [[key] for key in sub_menu.keys()]

    if path:
        reply_keyboard.append([MENU_ITEM_BACK])
        reply_keyboard.append([MENU_ITEM_HOME])

    return reply_keyboard


def get_sub_menu(path):
    sub_menu = menu

    if path:
        for key in path.split('.'):
            sub_menu = sub_menu.get(key)

    return sub_menu


def action_search(update, context):
    return actions.products_search(update, context)


def action_list(update, context):
    return actions.products_list(update, context)


def action_brands(update, context):
    return actions.brands_list(update, context)


def action_catalog(update, context):
    return actions.products_catalog(update, context)


def action_stub():
    pass
