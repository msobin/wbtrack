from common.models import *
from common.session import session
from wbbot.misc.product_card import get_price_icon, get_product_markup, get_size_list


def check_prices(context):
    user_product_prices = session.query(UserProductPrice).filter_by(status=UserProductPrice.STATUS_UPDATED).all()

    for user_product_price in user_product_prices:
        product = user_product_price.product

        user_products = session.query(UserProduct).filter_by(product_id=product.id).join(UserProduct.settings).filter(
            UserProductSettings.is_price_notify == True).all()

        user_product_price.status = UserProductPrice.STATUS_PROCESSED
        user_product_price.price_start = user_product_price.price_end

        if len(user_products):
            diff = abs(
                user_product_price.price_start - user_product_price.price_end) / user_product_price.price_start * 100

            price_icon = get_price_icon(user_product_price.price_end, user_product_price.price_start)
            cur_price = ProductPrice.format_price_value(user_product_price.price_end, product.domain)
            prev_price = ProductPrice.format_price_value(user_product_price.price_start, product.domain)

            price_text = f'{prev_price} → {cur_price}'

            for user_product in user_products:
                text = f'⚠️ Обновилась цена на {product.header}\n\n{price_icon} {price_text}'

                if product.size_list:
                    text += '\n' + get_size_list(product)

                reply_markup = get_product_markup(user_product.user.id, product)

                context.job_queue.run_once(notify_user, 1,
                                           context={'telegram_id': user_product.user.telegram_id, 'text': text,
                                                    'reply_markup': reply_markup})

    session.commit()


def notify_user(context):
    context.bot.send_message(context.job.context['telegram_id'], context.job.context['text'], parse_mode='HTML',
                             reply_markup=context.job.context['reply_markup'])
