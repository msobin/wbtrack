from telegram import ReplyKeyboardMarkup

import wbbot.actions.common as actions


def action_search(update, context):
    return actions.products_search(update, context)


def action_list(update, context):
    return actions.products_list_all(update, context)


def action_brands(update, context):
    return actions.brands_list(update, context)


def action_catalog(update, context):
    return actions.products_catalog(update, context)


def action_products_with_notify(update, context):
    return actions.product_list_by_notify(update, context, True)


def action_products_without_notify(update, context):
    return actions.product_list_by_notify(update, context, False)


def action_stub():
    pass


PATH_DELIMITER = '.'
MENU_ITEM_HOME = '🏠 Главное меню'
MENU_ITEM_BACK = '🔙 Назад'

# menu = {
#     '🛍️ Товары': {
#         '🔍 Найти': {
#             '👀 По названию': action_search,
#             '🔔 С уведомлениями': action_products_with_notify,
#             '🔕 Без уведомления': action_products_without_notify,
#         },
#         '📃 Список': action_list,
#         '🗂️ Каталог': action_catalog,
#         '👓 Брэнды': action_brands,
#     },
#     '⚙️ Настройки': 'action_stub',
# }

menu = {
    '🔍 Найти': {
        '👀 По названию': action_search,
        '🔔 С уведомлениями': action_products_with_notify,
        '🔕 Без уведомления': action_products_without_notify,
    },
    '📃 Список': action_list,
    '🗂️ Каталог': action_catalog,
    '👓 Брэнды': action_brands,
}


def menu_item_select(update, context):
    item = update.message.text
    path = context.user_data.get('menu_path')

    if item == MENU_ITEM_HOME:
        path = None
    elif item == MENU_ITEM_BACK:
        path = PATH_DELIMITER.join(path.split(PATH_DELIMITER)[:-1]) if path else None
    else:
        path = PATH_DELIMITER.join([path, item]) if path else item

    sub_menu = get_sub_menu(path)

    if not sub_menu:
        sub_menu = menu
        path = None

    if type(sub_menu) is dict:
        reply_keyboard = get_reply_keyboard(path)
    else:
        if callable(sub_menu):
            return sub_menu(update, context)
        else:
            return

    context.user_data['menu_path'] = path

    return update.message.reply_text(item, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))


def get_reply_keyboard(path):
    sub_menu = get_sub_menu(path)

    reply_keyboard = [[key] for key in sub_menu.keys()]

    if path:
        if path.count(PATH_DELIMITER):
            reply_keyboard.append([MENU_ITEM_BACK])
        reply_keyboard.append([MENU_ITEM_HOME])

    return reply_keyboard


def get_sub_menu(path):
    sub_menu = menu

    if path:
        for key in path.split(PATH_DELIMITER):
            sub_menu = sub_menu.get(key)

    return sub_menu
