from app.common.models import ProductPrice, User, UserProduct
from app.common.session import session
from app.wbbot.misc.product_card import get_price_icon, get_product_markup


def check_prices(context):
    product_prices = session.query(ProductPrice).filter_by(status=ProductPrice.STATUS_NEW).all()

    if not product_prices:
        return

    for product_price in product_prices:
        product = product_price.product

        if not product.previous_price:
            product_price.status = ProductPrice.STATUS_PROCESSED
            continue

        price_icon = get_price_icon(product.current_price_value, product.previous_price_value)
        prev_price = ProductPrice.format_price_value(product.previous_price_value, product.domain)
        cur_price = ProductPrice.format_price_value(product.current_price_value, product.domain)

        price_text = f'{prev_price} → {cur_price}'

        user_products = session.query(UserProduct).filter_by(product_id=product.id).all()

        if not len(user_products):
            product_price.status = ProductPrice.STATUS_PROCESSED
        else:
            for user_product in user_products:
                text = f'⚠️ Обновилась цена на {product.header}\n\n{price_icon} {price_text}'
                reply_markup = get_product_markup(user_product.user.id, product)

                context.job_queue.run_once(notify_user, 1,
                                           context={'telegram_id': user_product.user.telegram_id, 'text': text,
                                                    'reply_markup': reply_markup})

            product_price.status = ProductPrice.STATUS_PROCESSED

    session.commit()


def notify_user(context):
    context.bot.send_message(context.job.context['telegram_id'], context.job.context['text'], parse_mode='HTML',
                             reply_markup=context.job.context['reply_markup'])
