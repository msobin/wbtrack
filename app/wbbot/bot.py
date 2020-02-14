# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import wbbot.handlers.actions as actions
import wbbot.handlers.commands as commands
import wbbot.handlers.messages as messages
import common.env as env
import wbbot.misc.jobs as jobs
import logging.config
import random
import threading

from telegram.error import NetworkError

logging.basicConfig(filename=env.LOG_DIR + '/bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def start_pooling(proxy_url=None):
    request_kwargs = {'proxy_url': proxy_url} if proxy_url else {}

    updater = Updater(env.BOT_TOKEN, use_context=True, request_kwargs=request_kwargs)

    job_queue = updater.job_queue
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('ping', commands.command_ping))
    dispatcher.add_handler(CommandHandler(['start', 'help'], commands.command_start))
    dispatcher.add_handler(CommandHandler('list', commands.command_list))
    dispatcher.add_handler(CommandHandler('search', commands.command_search))
    dispatcher.add_handler(CommandHandler('brands', commands.command_brands))
    dispatcher.add_handler(CommandHandler('catalog', commands.command_catalog))
    dispatcher.add_handler(CommandHandler('logout', commands.command_logout))

    dispatcher.add_handler(MessageHandler(Filters.reply, messages.message_search))
    dispatcher.add_handler(MessageHandler(Filters.regex(env.PRODUCT_REGEXP), messages.message_add_product))

    dispatcher.add_handler(CallbackQueryHandler(actions.inline_callback))

    job_queue.run_repeating(jobs.check_prices, env.NOTIFY_INTERVAL, 1)

    if proxy_url:
        # try to restart without proxy after N seconds
        threading.Timer(60 * 30, restart_pooling_by_timer, [updater]).start()

    updater.start_polling()
    updater.idle()


def restart_pooling_by_timer(*args):
    logging.info('Trying to reconnect without proxy')
    updater, = args
    updater.stop()
    start_pooling(None)


def main():
    proxy_url = None

    while True:
        try:
            start_pooling(proxy_url)
        except NetworkError:
            # retry connect with random proxy
            logging.error('Connection error, trying to use proxy')

            with open(env.DATA_DIR + '/proxies.lst') as f:
                proxies = f.readlines()
            proxy_url = 'https://' + random.choice(proxies).strip()

            logging.info('Trying to connect over proxy: ' + proxy_url)

            continue

        break


if __name__ == "__main__":
    main()
