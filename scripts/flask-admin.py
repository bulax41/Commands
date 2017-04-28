#!/usr/bin/env python

import peewee
import struct
import socket
from peewee import *
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView

app = Flask(__name__)
db = MySQLDatabase('ddos',host="10.74.74.31",user="filter",passwd="VDIware123")

class DBModel(Model):
        class Meta:
                database = db
class IP(DBModel):
        id = PrimaryKeyField()
        ip = IntegerField()
        modified = TimestampField()

        def __str__(self):
            return ip2ascii(self.ip)

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
        valid = DateTimeField()


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

class FirewallModelView(ModelView):
    can_delete = False
    can_create = True
    can_edit = True
    create_modal = True
    edit_modal = True
    can_view_details = True
    can_export = True
    page_size = 100

class RuleAdmin(FirewallModelView):
    #column_searchable_list = ['ip']
    #column_filters = ['ip']
    can_delete = False
    column_filters = ('deleted',)

def ip2ascii(ip):
    return socket.inet_ntoa(struct.pack('!L', ip))

class IPAdmin(FirewallModelView):

    def _ip_formatter(view, context, model, name):
        return socket.inet_ntoa(struct.pack('!L', model.ip))

    column_formatters = {
        'ip': _ip_formatter
    }

    column_labels = {
        'ip':'IP Address'
    }

    column_default_sort = 'ip'


class FilterAdmin(FirewallModelView):
    can_delete = True

class NetworkAdmin(FirewallModelView):
    can_delete = True


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

if __name__ == '__main__':
        admin = Admin(app, name='Firewall')
        admin.add_view(IPAdmin(IP))
        admin.add_view(NetworkAdmin(Network))
        admin.add_view(FilterAdmin(Filter))
        admin.add_view(RuleAdmin(Rule))
        app.run()
