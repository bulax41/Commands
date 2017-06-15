#!/bin/python
import subprocess
import select
import sys
import datetime
import time
import re
import json

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

savefile = "chatlist.json"
user_token = "8c6d20cee7837fa7e6a55a254aa3ac53"
admin_token = "79e36a012213b96a2248cefe01225f71"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def _messageUsers(message):
    return

def _messageAdmins(message):
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
                userList[str(user.id)]["admin"] = True
                update.message.reply_text("%s, you are now an admin. Wield the power with care.  Check out the /help menu to see the new commands." % user.first_name)
                return
        _add_user(update,admin=True)
    else:
        update.message.reply_text("Hi %s, I don't think chatting with you is a good idea. " % user.first_name )
        return

    update.message.reply_text("Welcome %s! If you need help just ask. /help" % user.first_name)

    _messageAdmins(user.first_name)

    return


def blackhole(bot, update, args):
    global bh_ips
    msg = ""
    if _auth(update) == False:
        return

    if _auth(update,admin=True) == True:
        output=subprocess.check_output(["/root/blackhole.sh"," ".join(args)])
        update.message.reply_text("%s blackholed" % output)

        if output.find("Sucess") != -1:
            bh_ips.append(args)
            msg = "I have blackhole %s" % " ".join(args)
        else:
            msg = output
    else:
        msg = "Hmmm...  Let me check to see if I can do that for you."

    update.message.reply_text(msg)

def bhlist(bot, update):
    global bh_ips
    if _auth(update) == False:
        return

    ips = "\n".join(bh_ips)
    text = "List of Blackholed IP's:\n %s " % ips
    update.message.reply_text(text)


def help(bot, update):
    global userList
    if _auth(update) == False:
        return

    user = update.message.from_user
    if _auth(update,admin=True):
        m = """
        *Admin Commands*
        /blackhole {IP}    : This will blackhole the IP on the network and with our upstream peeers
        /tokens   :  Replies with the registration tokens
        """
        update.message.reply_text(m)

    update.message.reply_text(
        """
        *User menu*
        /bhlist  :  List the IP's currently blackholed on the network.
        /who   : List the registered users.
        /register {token}  : This is to register with the Bot or upgrade an account to an admin.
        """
        )

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    global userList
    userList = []

    # open up pipe to receive alerts
    FIFO="/tmp/telegram.bot"
    try:
        os.mkfifo(FIFO)
    except OSError as oe:
        if oe.errno != errno.EEXIST:
            raise

    try:
        with open(savefile, 'r') as f:
            try:
                userList = json.load(f)
            except ValueError:
                print "No users to load"
                pass
    except:
        pass


    # Create the EventHandler and pass it your bot's token.
    updater = Updater("284345903:AAEjNSN0fFgSPMcNPns5rRjVw8rWXOFWek0")

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

    keepRunning = 1
    pollPeriod = 0.75
    maxAtOnce = 50

    while keepRunning == 1:
        while keepRunning and sys.stdin in select.select([sys.stdin], [], [], pollPeriod)[0]:
            msgs = []
            msgsInBatch = 0
            while keepRunning and sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline()
                if line:
                    msg = line.split()
                    #m = search.match(line)
                    if len(msg) > 4:
                        if msg[3]=="DDoS":
                           message = "Possible DDoS: IP %s, Router %s, Peer %s\n" % (msg[11],msg[1],peers[msg[1]][msg[7]])
                           msgs.append(message)
                else:
                    # Stdin is closed
                    keepRunning = 0

                if len(msgs) > 0:
                    for user in userList:
                        chat_id = userList[user]["chat_id"]
                        try:
                            updater.bot.sendMessage(chat_id=chat_id,text="\n".join(msgs))
                        except Unauthorized:
                            # remove update.message.chat_id from conversation list
                            chatList.remove(chat_id)
                            continue
                        except BadRequest:
                            # remove update.message.chat_id from conversation list
                            continue
                        except TimedOut:
                            # handle slow connection problems
                            continue
                        except NetworkError:
                            # handle other connection problems
                            continue
                        except ChatMigrated as e:
                            chatList.remove(chat_id)
                            chatList.append(e)
                            continue
                        except TelegramError:
                            # handle all other telegram related errors
                            continue

    time.sleep(3)
    updater.stop()

if __name__ == '__main__':
    main()
