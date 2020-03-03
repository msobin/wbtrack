from common.models import *
from common.session import session
from wbbot.misc.product_card import get_price_icon, get_product_markup, get_size_list


def check_prices(context):
    user_product_prices = session.query(UserProductPrice).filter(
        UserProductPrice.status.in_([UserProductPrice.STATUS_APPEARED, UserProductPrice.STATUS_UPDATED])).join(
        UserProductSettings, UserProductPrice.user_product_id == UserProductSettings.user_product_id).filter(
        UserProductSettings.is_price_notify == True).all()

    for user_product_price in user_product_prices:
        product = user_product_price.user_product.product
        user_product = user_product_price.user_product

        diff_perc = abs(
            user_product_price.price_start - user_product_price.price_end) / user_product_price.price_start * 100

        price_icon = get_price_icon(user_product_price.price_end, user_product_price.price_start)
        cur_price = ProductPrice.format_price_value(user_product_price.price_end, product.domain)
        prev_price = ProductPrice.format_price_value(user_product_price.price_start, product.domain)

        if prev_price == cur_price:
            price_text = cur_price
        else:
            price_text = f'{prev_price} → {cur_price}'

        text = f'⚠️ Обновилась цена на {product.header}\n\n{price_icon} {price_text}'

        if product.size_list:
            text += '\n' + get_size_list(product)

        reply_markup = get_product_markup(user_product.user.id, product)
        context.job_queue.run_once(notify_user, 1,
                                   context={'telegram_id': user_product.user.telegram_id, 'text': text,
                                            'reply_markup': reply_markup})

        user_product_price.status = UserProductPrice.STATUS_PROCESSED
        user_product_price.price_start = user_product_price.price_end

    session.commit()


def notify_user(context):
    context.bot.send_message(context.job.context['telegram_id'], context.job.context['text'], parse_mode='HTML',
                             reply_markup=context.job.context['reply_markup'])
