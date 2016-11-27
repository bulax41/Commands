#!/bin/python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import subprocess
import select
import sys
import datetime
import time
import re

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    global chatList
    update.message.reply_text('Hio!')
    chat_id =  update.message.chat.id
    if chat_id not in chatList:
        chatList.append(chat_id)

def blackhole(bot, update, args):
    global bh_ips
    output=subprocess.check_output(["/root/blackhole.sh"," ".join(args)])
    update.message.reply_text("%s blackholed" % output)

    if output.find("Sucess") != -1:
        bh_ips.append(args)

def bhlist(bot, update):
    global bh_ips
    ips = "\n".join(bh_ips)
    text = "List of Blackholed IP's:\n %s " % ips
    update.message.reply_text(text)


def help(bot, update):
    update.message.reply_text('I am not going to help you.')
    logger.info('Help was requested')

def echo(bot, update):
    global chatList
    update.message.reply_text(update.message.text)
    chat_id =  update.message.chat.id
    if chat_id not in chatList:
        chatList.append(chat_id)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    global chatList
    chatList = []

    # Create the EventHandler and pass it your bot's token.
    updater = Updater("284345903:AAEjNSN0fFgSPMcNPns5rRjVw8rWXOFWek0")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("bhlist", bhlist))
    dp.add_handler(CommandHandler("blackhole", blackhole,pass_args=True))

    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # search

    updater.idle()

if __name__ == '__main__':
    main()
