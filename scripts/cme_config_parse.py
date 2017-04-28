#!/usr/bin/env python
import argparse
from ftplib import FTP
import xml.etree.ElementTree
from StringIO import StringIO

parser = argparse.ArgumentParser(description='Parse the CME\'s config.xml file.  With no arguments it just prints out all channel ID\'s and labels')
parser.add_argument('-c', '--channel', type=int, help="Channel number to print out details")
args = parser.parse_args()

cfile = StringIO()
ftp = FTP('ftp.cmegroup.com')
ftp.login()
ftp.retrbinary('RETR SBEFix/Production/Configuration/config.xml', cfile.write)

e = xml.etree.ElementTree.fromstring(cfile.getvalue())

if args.channel:
    for channel in e:
        if int(channel.attrib['id'])==args.channel:
            print "Channel ID: %s, Label: %s" % (channel.attrib['id'],channel.attrib['label'])
            for connections in channel.findall('connections'):
                for connection in connections.findall('connection'):
                    if connection.find('protocol').text=="UDP/IP":
                        print "\tFeed %s, Type %s, %s:%s " % \
                            (
                            connection.find('feed').text,
                            connection.find('type').text,
                            connection.find('ip').text,
                            connection.find('port').text
                            )

else:
    for channel in e:
        print "Channel %s, Label: %s" % (channel.attrib['id'],channel.attrib['label'])
