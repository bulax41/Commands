#!/usr/bin/env python

import subprocess
import select
import sys
import datetime
import time
import re
import json
import socket
import logging
import telegram
from contextlib import closing
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

savefile = "chatlist.json"
user_token = "8c6d20cee7837fa7e6a55a254aa3ac53"
admin_token = "79e36a012213b96a2248cefe01225f71"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def _messageUsers(message):
    global userList,updater
    for user in userList.keys():
        chat_id = userList[user]["chat_id"]
        try:
            logger.info("Sending Message to user %s" % user)
            updater.bot.sendMessage(chat_id=chat_id,text=message)

        except Unauthorized:
            # remove update.message.chat_id from conversation list
            chatList.remove(chat_id)
            logger.warning("Unauthorized, remove update.message.chat_id from conversation list")
            continue
        except BadRequest:
            # remove update.message.chat_id from conversation list
            logger.warning("BadRequest, sending message")
            continue
        except TimedOut:
            # handle slow connection problems
            logger.warning("TimedOut, sending message")
            continue
        except NetworkError:
            # handle other connection problems
            logger.warning("NetworkError, sending message")
            continue
        except ChatMigrated as e:
            logger.warning("Chat Migrated ID, sending message")
            continue
        except TelegramError:
            # handle all other telegram related errors
            logger.warning("TelegramError, sending message")
            continue
    return

def _messageAdmins(message):
    global userList,updater
    for user in userList.keys():
        if userList[user]["admin"] == False:
            continue
        chat_id = userList[user]["chat_id"]
        try:
            logger.info("Sending Message to user %s" % user)
            updater.bot.sendMessage(chat_id=chat_id,text=message)

        except Unauthorized:
            # remove update.message.chat_id from conversation list
            chatList.remove(chat_id)
            logger.warning("Unauthorized, remove update.message.chat_id from conversation list")
            continue
        except BadRequest:
            # remove update.message.chat_id from conversation list
            logger.warning("BadRequest, sending message")
            continue
        except TimedOut:
            # handle slow connection problems
            logger.warning("TimedOut, sending message")
            continue
        except NetworkError:
            # handle other connection problems
            logger.warning("NetworkError, sending message")
            continue
        except ChatMigrated as e:
            logger.warning("Chat Migrated ID, sending message")
            continue
        except TelegramError:
            # handle all other telegram related errors
            logger.warning("TelegramError, sending message")
            continue
    return

def tokens(bot,update):
    if _auth(update,admin=True) == False:
        return

    update.message.reply_text(
        """
        User registration token: %s
        Admin registration token: %s
        """ % (user_token,admin_token)
        )
    return


def who(bot,update):
    global userList
    if _auth(update) == False:
        return

    for user in userList.keys():
        admin = ""
        if userList[user]["admin"]:
            admin = ", Admin"
        msg = "%s %s, %s %s" % (userList[user]["first_name"],userList[user]["last_name"],userList[user]["username"],admin)
        update.message.reply_text(msg)
    return

def _auth(update,admin=False):
    global userList
    user = update.message.from_user

    if update.message.chat.type != "private":
        update.message.reply_text("Sorry %s, I prefer only private chats." % user.first_name)
        return(False)

    if userList.has_key(str(user.id)):
        if admin:
            return(userList[str(user.id)]["admin"])
        return(True)

    update.message.reply_text("I'm sorry %s.  I am not sure chatting with you is a good idea right now." % user.first_name)
    return(False)

def _add_user(update,admin=False):
    global userList
    userList[str(update.message.from_user.id)] = {
        "admin":admin,
        "chat_id":update.message.chat.id,
        "first_name": update.message.from_user.first_name,
        "last_name": update.message.from_user.last_name,
        "username": update.message.from_user.username
    }

    with open(savefile, 'w') as f:
        json.dump(userList,f)

    return

def register(bot, update, args):
    global userList
    user = update.message.from_user

    token = " ".join(args)
    if token == user_token:
        if userList.has_key(str(user.id)):
            update.message.reply_text("%s, you have already registered." % user.first_name)
            return
        _add_user(update)
    elif token == admin_token:
        if userList.has_key(str(user.id)):
            if userList[str(user.id)]["admin"]:
                update.message.reply_text("%s, you are already and admin." % user.first_name)
                return
            else:
                _add_user(update,admin=True)
                update.message.reply_text("%s, you are now an admin. Wield the power with care.  Check out the /help menu to see the new commands." % user.first_name)
                return
    else:
        update.message.reply_text("Hi %s, I can't register you. " % user.first_name )
        return

    update.message.reply_text("Welcome %s! If you need help just ask. /help" % user.first_name)

    _messageAdmins(user.first_name)

    return


def help(bot, update):
    global userList
    if _auth(update) == False:
        return

    user = update.message.from_user
    if _auth(update,admin=True):
        m = """
        *Admin Commands*
        /tokens   :  Replies with the registration tokens
        """
        update.message.reply_text(m)

    update.message.reply_text(
        """
        *User menu*
        /who   : List the registered users.
        /register {token}  : This is to register with the Bot or upgrade an account to an admin.
        """
        )

def echo(bot, update):
    if _auth(update) == False:
        return

    update.message.reply_text(update.message.text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def unknownCmd(bot, update):
    if _auth(update) == False:
        return
    update.message.reply_text("Hi %s, not sure I understand, please ask for /help if needed." % update.message.from_user.first_name)
    return

def load_users():
    global userList
    # open up previous authenticated chat users
    try:
        with open(savefile, 'r') as f:
            try:
                userList = json.load(f)
            except ValueError:
                print "No users to load"
                pass
    except:
        pass

def main():
    global userList,updater
    userList = {}

    load_users()
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("319507063:AAFI9Ca2x50NKTxBuxOn5TSHvdEI-bng0N4")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("register", register,pass_args=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("who", who))
    dp.add_handler(CommandHandler("tokens", tokens))

    dp.add_handler(MessageHandler(Filters.command,help))
    dp.add_handler(MessageHandler(Filters.text, help))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
