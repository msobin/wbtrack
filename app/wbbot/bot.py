# -*- coding: utf-8 -*-
import logging
import time
from logging.handlers import TimedRotatingFileHandler

from telegram.error import NetworkError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

import common.env as env
import wbbot.handlers.actions as actions
import wbbot.handlers.commands as commands
import wbbot.handlers.messages as messages
import wbbot.misc.jobs as jobs
import wbbot.handlers.menu as menu


def main():
    # logging.basicConfig(level=logging.INFO,
    #                     handlers=[TimedRotatingFileHandler(filename=env.LOG_DIR + '/bot.log', when='midnight',
    #                                                        backupCount=7)],
    #                     format='%(asctime)s - %(levelname)s - %(message)s')

    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    updater = Updater(env.BOT_TOKEN, use_context=True)
    job_queue = updater.job_queue
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('ping', commands.command_ping))
    dispatcher.add_handler(CommandHandler(['start', 'help'], commands.command_start))
    dispatcher.add_handler(CommandHandler('list', commands.command_list))
    dispatcher.add_handler(CommandHandler('search', commands.command_search))
    dispatcher.add_handler(CommandHandler('brands', commands.command_brands))
    dispatcher.add_handler(CommandHandler('catalog', commands.command_catalog))
    dispatcher.add_handler(CommandHandler('logout', commands.command_logout))
    dispatcher.add_handler(CommandHandler('menu', menu.start))

    dispatcher.add_handler(MessageHandler(Filters.reply, messages.message_search))
    dispatcher.add_handler(MessageHandler(Filters.regex(env.PRODUCT_REGEXP), messages.message_add_product))

    dispatcher.add_handler(CallbackQueryHandler(actions.inline_callback))

    job_queue.run_repeating(jobs.check_prices, env.NOTIFY_INTERVAL, 1)

    try:
        updater.start_polling()
        updater.idle()
    except NetworkError as e:
        logging.error('Network error:' + e.message)
        time.sleep(60 * 5)


if __name__ == "__main__":
    main()
