from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def start(update, context):
    reply_keyboard = [['Boy'], ['Girl'], ['Other']]
    update.message.reply_text('test', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

