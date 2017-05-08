#!/usr/bin/python
import socket
import subprocess
import argparse
import sys
import datetime



parser = argparse.ArgumentParser(description='Ping with output starting with data and time of day')
parser.add_argument('ip', metavar="IP", help="IP Address to PING")
parser.add_argument('-f','--file',help="File to log output")
args = parser.parse_args()

try:
    socket.inet_aton(args.ip)
except:
    print "%s is not a valid IP" % args.ip
    sys.exit(1)

if args.file:
    try:
        log = open(args.file,"w",0)
    except:
        print "Could not open file for writing, %s" % args.file
        sys.exit(1)

cmd = ['/sbin/ping','-D', args.ip ]
ping = subprocess.Popen(cmd, stdout=subprocess.PIPE)
while True:
  line = ping.stdout.readline()
  if line != b'':
      out = "%s %s" % (datetime.datetime.now().strftime("%b %d %Y %X.%f"),line.rstrip())
      if args.file:
          log.write(out+"\n")
      else:
          print out
  else:
    break
