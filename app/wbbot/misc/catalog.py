import json

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def get_catalog(session, user_id, level, category_id=None):
    sql = f'select catalog_category_ids[{level}], count(catalog_category_ids[{level}]), cc.title from product\n' \
          f'right join catalog_category cc on cc.id = catalog_category_ids[{level}]\n' \
          f'where product.id in (select product_id from user_product where user_id={user_id})'

    if category_id:
        sql += f'and catalog_category_ids[{level-1}] = {category_id}'

    sql += f'\ngroup by catalog_category_ids[{level}], cc.title\n' \
           'order by cc.title'

    return session.execute(sql).fetchall()


def get_count_wo_category(session, user_id):
    sql = 'select count(*) from product\n' \
          f'where product.id in (select product_id from user_product where user_id={user_id})' \
          ' and catalog_category_ids is null'

    count, = session.execute(sql).fetchone()

    return count


def get_catalog_markup(rows):
    buttons = []

    for c_id, c_count, c_name in rows:
        if c_count == 0:
            continue

        buttons.append([InlineKeyboardButton(
            f'{c_name} ({c_count})',
            callback_data=json.dumps({'action': 'catalog_category', 'level': 2, 'id': c_id})
        )])

    return InlineKeyboardMarkup(buttons)
