#!/usr/bin/env python
import peewee
import struct
import socket
from peewee import *

db = MySQLDatabase('ddos',host="10.74.74.31",user="filter",passwd="VDIware123")

class DBModel(Model):
        class Meta:
                database = db
class IP(DBModel):
        id = PrimaryKeyField()
        ip = IntegerField()
        modified = TimestampField()

class Rule(DBModel):
        id = PrimaryKeyField()
        ip = ForeignKeyField(IP,related_name='rules')
        created = DateTimeField()
        modified = DateTimeField()
        recent = BooleanField()
        source = CharField()
        protocol = IntegerField()
        port = IntegerField()
        port_end = IntegerField()
        deleted = BooleanField()



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

def ip2ascii(ip):
    return socket.inet_ntoa(struct.pack('!L', ip))

def rule_print(ip,rule):
    out = "iptables -A FILTER-IP-%s -p %s -s %s " % (ip2ascii(ip.ip),rule.protocol,rule.source)
    if rule.port_end != 0:
        out = out + "-m multiport --dports %s:%s " % (rule.port,rule.port_end)
    elif rule.port != 0:
        out = out + "--dport %s " % rule.port
    if rule.recent == 1:
        out = out + "-m recent --set filter-%s " % ip2ascii(ip.ip)
    print out




db.connect()

# Loop through IP's joined with rules
for ip in IP.select():
        print "iptables -F FILTER-IP-%s" % ip2ascii(ip.ip)
        for rule in ip.rules:
                rule_print(ip,rule)
        print "iptables -A FILTER-IP-%s -j DROP" % ip2ascii(ip.ip)
