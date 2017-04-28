#!/usr/bin/env python
import peewee
import configparser
import struct
import socket
from peewee import *
import sys, getopt
import datetime

config = configparser.ConfigParser()
config.read('filter.ini')
db = MySQLDatabase(
    config['DB']['database'],
    host=config['DB']['host'],
    user=config['DB']['username'],
    passwd=config['DB']['password']
    )

class DBModel(Model):
        class Meta:
                database = db

class IP(DBModel):
        id = PrimaryKeyField()
        ip = IntegerField(unique=True)
        modified = DateTimeField(default=datetime.datetime.now)

class Rule(DBModel):
        id = PrimaryKeyField()
        ip = ForeignKeyField(IP,related_name='rules')
        created = DateTimeField(default=datetime.datetime.now)
        modified = DateTimeField(default=datetime.datetime.now)
        recent = BooleanField(default=True)
        source = CharField(default="0.0.0.0/0")
        protocol = IntegerField(default=6)
        port = IntegerField(default=0)
        port_end = IntegerField(default=0)
        deleted = BooleanField(default=0)

class Filter(DBModel):
        id = PrimaryKeyField()
        name = CharField()
        timestamp = TimestampField()

class Network(DBModel):
        id = PrimaryKeyField()
        network = IntegerField()
        prefix = IntegerField()
        filter = BooleanField()
        limit = IntegerField()
        burst = IntegerField()

def help(msg):
    print msg
    print ""
    print 'filter.py -a add -i <ip> -r <recent: 0 or 1> -p <protocol> [-s <source> -b <port> -e <port_end>]'
    print 'filter.py -a list -i <ip>'
    print 'filter.py -a delete -i <ip> -n <rule_number>'
    sys.exit(2)

def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

def ip2ascii(ip):
    return socket.inet_ntoa(struct.pack('!L', ip))

def main(argv):

    try:
        opts, args = getopt.getopt(argv,"a:i:r:p:s:b:e:n:c")
    except getopt.GetoptError as err:
        help(str(err))

    if args:
        help("Didn't understand '%s'" % " ".join(args))

    add = False
    ip = False
    for opt, arg in opts:
        if opt == "-i":
            ip = arg
        elif opt == "-a":
            action = arg
        elif opt == "-c":
            add = True
    if not ip:
        help("No IP specified.")

    try:
        ip_num = ip2long(ip)
    except:
        help("Invalid IP %s" % ip_num)

    try:
        db.connect()
    except:
        print "Could not connect to the database.  Check the filter.ini file settings"
        sys.exit(1)

    try:
        address = IP.get(IP.ip==ip_num)
    except IP.DoesNotExist:
        if add:
            try:
                address = IP(ip=ip_num)
                address.save()
            except:
                print "Something went wrong.  Could not create IP %s record" % ip2ascii(ip_num)
                sys.exit(1)
        else:
            print "IP %s not in database. To add IP include the -c option" % ip2ascii(ip_num)
            sys.exit(1)


    if action == "add":
        rule = Rule()
        protocol=0
        recent=1
        for opt, arg in opts:
            if opt == "-p":
                rule.protocol = arg
            elif opt == "-s":
                rule.source = arg
            elif opt == "-b":
                rule.port = arg
            elif opt == "-e":
                rule.port_end = arg
            elif opt == "-r":
                if arg == 0 or arg == 1:
                    rule.recent = arg
                else:
                    print ""
        try:
            rule.ip = address
            rule.save()
        except:
            print "Something went wrong.  Could not save rule."

    elif action == "list":
        try:
            print "{0:6} {1:8} {2:5} {3:8} {4:15} {5:6}".format("Rule","Protocol","Port","Port_End","Source","Recent")
            for rule in address.rules:
                recent = "Yes"
                if rule.recent == 0:
                    recent = "No"
                print "{0:6d} {1:8} {2:5} {3:8}  {4:15} {5:6}".format(rule.id,rule.protocol,rule.port,rule.port_end,rule.source,recent)
        except:
            print "No rules for %s" % ip2ascii(ip_num)

    elif action == "delete":
        rule_id = 0
        for opt, arg in opts:
            if opt == "-n":
                rule_id = arg
        if rule_id == 0:
            help("No rule id supplied.")

        try:
            rule = Rule.get(Rule.id==rule_id)
            rule.delete_instance()
        except Rule.DoesNotExist:
            print "Rule %s does not exist for IP %s" % (rule_id,ip2ascii(ip_num))

    else:
        help("")


if __name__ == "__main__":
   main(sys.argv[1:])
