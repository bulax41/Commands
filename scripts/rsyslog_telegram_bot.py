#!/usr/bin/env python
import subprocess
import select
import sys
import datetime
import time
import re
import json
import logging
import threading
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram_bot

savefile = "chatlist.json"
user_token = "8c6d20cee7837fa7e6a55a254aa3ac53"
admin_token = "79e36a012213b96a2248cefe01225f71"


def top_talkers():
    global stats, stats_pps, stats_bps


def speed_calc(old,new,time):
    rate = (int(new)-int(old))/int(time)
    return rate

def pmacct():
    global updater
    tsleep = 10
    stats = {}
    stats_pps = {}
    stats_bps = {}

    while True:

        pmacct_output = subprocess.check_output(['/usr/local/bin/pmacct','-s','-p','/tmp/pmacct.in'])
        for line in string.split(pmacct_output,'\n'):
                if string.find(line,"46.235") != -1:
                        line_array = string.split(line)
                        if line_array[0]  in stats:
                                stats_pps[line_array[0]] = speed_calc(stats[line_array[0]]["packets"], line_array[1],tsleep)
                                stats_bps[line_array[0]] = speed_calc(stats[line_array[0]]["bytes"], line_array[2],tsleep)
                                stats[line_array[0]]["packets"] = line_array[1]
                                stats[line_array[0]]["bytes"] = line_array[2]
                        else:
                                stats[line_array[0]] = {"packets": line_array[1], "bytes": line_array[2], "pps":0, "bps":0}
                                stats_pps[line_array[0]] = 0
                                stats_bps[line_array[0]] = 0

        hosts = stats.keys()
        hosts.sort()
        for host in hosts:
                if stats_bps[host] > 1000000:
			_messageAdmins("%s PPS %s, bits/s %s" % (host,stats_pps[host],stats_bps[host]))
        time.sleep(tsleep)


def blackhole(bot, update, args):
    global bh_ips
    msg = ""
    if _auth(update) == False:
        return

    if _auth(update,admin=True) == True:
	ip = " ".join(args)
        output=subprocess.check_output(["/root/blackhole.sh",ip])

        if output.find("Sucess") != -1:
            bh_ips.append(ip)
            msg = "I have blackhole %s" % ip
        else:
            msg = output
    else:
        msg = "Hmmm...  Let me check to see if I can do that for you."

    update.message.reply_text(msg)

def bhremove(bot,update,args):
    global bh_ips
    if _auth(update) == False:
        return

    if _auth(update,admin=True) == True:
        ip = " ".join(args)
        output=subprocess.check_output(["/root/blackhole.sh","remove",ip])

        if output.find("Sucess") != -1:
            bh_ips.append(ip)
            msg = "%s has been removed" % ip
        else:
            msg = output
    else:
        msg = "Hmmm...  Let me check to see if I can do that for you."

    update.message.reply_text(msg)

def bgp_summary(bot,update):
    if _auth(update) == False:
        return

    output=subprocess.check_output(["vtysh","-c","show ip bgp summary"])
    update.message.reply_text(output)



def bhlist(bot, update):
    global bh_ips
    if _auth(update) == False:
        return

    ips = "\n".join(bh_ips)
    text = "List of Blackholed IP's:\n %s " % ips
    update.message.reply_text(text)

def talk(bot,update):
    update.message.reply_text("I am not a very talkative bot.  Ask for /help  and tell me what to do.")

def help(bot, update):
    global userList
    if _auth(update) == False:
        return

    user = update.message.from_user
    if _auth(update,admin=True):
        m = """
        *Admin Commands*
        /blackhole {IP}    : This will blackhole the IP on the network and with our upstream peeers
        /bhremove {IP}     : This will remove the IP from the blackhole list
        /tokens   :  Replies with the registration tokens
        """
        update.message.reply_text(m)

    update.message.reply_text(
        """
        *User menu*
        /bhlist  :  List the IP's currently blackholed on the network.
	    /bgp_peers : List rt04-wan-ld4 bgp peers summary
        /who   : List the registered users.
        /register {token}  : This is to register with the Bot or upgrade an account to an admin.
        """
        )

def error(bot, update, error):
    telegram_bot.logger.warn('Update "%s" caused error "%s"' % (update, error))

def ping(bot, update, args):
    if _isIPv4(args[0]):
        try:
            output=subprocess.check_output(["ping","-c 5","-i .2",args[0]],stderr=subprocess.STDOUT)
            reply_markup = telegram.ReplyKeyboardMarkup([["Yes", "No","5","/traceroute"]],one_time_keyboard=True)
            button1 = telegram.InlineKeyboardButton(text="Yes",callback_data="8.8.8.8")
            button2 = telegram.InlineKeyboardButton(text="No",callback_data="1.1.1.1")
            inline_markup = telegram.InlineKeyboardMarkup([[button1],[button2]])
            update.message.reply_text(output,reply_markup=inline_markup)
        except subprocess.CalledProcessError,o:
            update.message.reply_text(o.output)
    else:
        update.message.reply_text("Thats not a valid IP")
    return

def traceroute(bot, update, args):
    if len(args) != 1:
        help(bot,update)
        return
    if _isIPv4(args[0]):
        update.message.reply_text("tracing up to 20 hops..")
        try:
            output=subprocess.check_output(["traceroute","-In","-q","1","-w","1","-m","20",args[0]],stderr=subprocess.STDOUT)
            update.message.reply_text(output)
        except subprocess.CalledProcessError,o:
            update.message.reply_text(o.ouput)
    else:
        update.message.reply_text("Thats not a valid IP")
    return

def _isValidPort(port):
    try:
        _port = int(port)
    except:
        return False
    if(int(_port)>0 and int(_port)<65536):
        return True

    return False


def port(bot,update,args):
    if len(args) != 2:
        help(bot,update)
        return
    if not _isValidPort(args[1]):
        update.message.reply_text("Thats not a valid Port")
        return

    if _isIPv4(args[0]):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(1)
            if sock.connect_ex((args[0], int(args[1]))) == 0:
                update.message.reply_text("Port %s:%s Open" % (args[0],args[1]))
            else:
                update.message.reply_text("Port %s:%s Closed" % (args[0],args[1]))
    else:
        update.message.reply_text("Thats not a valid IP")
    return

def _isIPv4(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False

def syslog_listen():
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
                        if len(msg) > 4:
                            #if msg[3]=="DDoS":
                               message = "Possible DDoS: IP %s, Router %s, Peer %s\n" % (msg[11],msg[1],peers[msg[1]][msg[7]])
                               msgs.append(message)
                               logger.info(message)
                    else:
                        # Stdin is closed
                        keepRunning = 0

                if len(msgs) > 0:
                    _messageAdmins(msgs.join("\n"))

def main():
    global userList,bh_ips,stats,stats_pps,stats_bps,updater
    stats = {}
    stats_pps = {}
    stats_bps = {}
    userList = {}
    peers = {
        'rt01-wan-ld5' : { 'IN=ens1d1' : 'GTT', 'IN=ens1d2' : 'LINX' },
        'rt02-wan-ld5' : { 'IN=ens1d1' : 'Cogent' }
    }

    telegram_bot.load_users()

    # Populate the blackhole list
    #sublist = subprocess.check_output(["/root/blackhole.sh","list"])
    #bh_ips = sublist.split()

    # Create the EventHandler and pass it your bot's token.
    updater = Updater("284345903:AAEjNSN0fFgSPMcNPns5rRjVw8rWXOFWek0")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("register", telegram_bot.register,pass_args=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("bhlist", bhlist))
    dp.add_handler(CommandHandler("blackhole", blackhole,pass_args=True))
    dp.add_handler(CommandHandler("bhremove", bhremove,pass_args=True))
    dp.add_handler(CommandHandler("who", telegram_bot.who))
    dp.add_handler(CommandHandler("tokens", telegram_bot.tokens))
    dp.add_handler(CommandHandler("bgp_peers",bgp_summary))
    dp.add_handler(CommandHandler("top_talkers",top_talkers))

    dp.add_handler(MessageHandler(Filters.command,help))
    dp.add_handler(MessageHandler(Filters.text, talk))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    t1 = threading.Thread(target=syslog_listen, args=())
    t2 = threading.Thread(target=pmacct, args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    time.sleep(3)
    updater.stop()

if __name__ == '__main__':
    main()
