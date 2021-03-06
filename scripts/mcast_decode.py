#!/usr/bin/env  python
import socket
import struct
import sys
import signal
import time
import datetime
import argparse
from mcast_listen import *

def signal_handler(signal, frame):
        global estop
        estop.set()
        sys.exit(0)

def decode_cme(msg):
   return  struct.unpack_from("IQ",msg)

def decode_lmax(msg):
   (sessionid,seqnum,msglength,msgtype,msgseqnum,timesec,timenanos) = struct.unpack_from("<IQHHQII",msg)
   pcktime = int(timesec) + int(timenanos)
   return (seqnum,pcktime)

def join_group_cme(group,args,event):
    global count
    (mcast_group,mcast_port) = group.split(":")
    sock = McastSocket(local_port=int(mcast_port),reuse=1)
    sock.mcast_add(mcast_group, args.interface)
    stime= datetime.datetime.now()
    print "Joining %s:%s at %s" % (mcast_group,mcast_port,stime.strftime("%b %d %Y %X.%f"))


    MsgSeqNum = 0
    while not event.isSet():

        try:
            sock.settimeout(30.0)
            msg,source = sock.recvfrom(1500)
        except socket.timeout:
            print "Timeout on %s at %s", % (group,datetime.datetime.now().strftime("%b %d %Y %X.%f"))
            continue

        (Num,Time) = decode_cme(msg)

        diff = int(Num) - MsgSeqNum
        if MsgSeqNum == 0:
                print "Decoding %s %s, Initial sequene number: %s" % (args.decode,group,int(Num))
        elif diff!=1:
                now =  datetime.datetime.now().strftime("%b %d %Y %X.%f")
                print "Gapped Detected %s, %s Packets, Sequence Numbers %s-%s at %s" %  (group,diff-1,MsgSeqNum+1,int(Num)-1,now)
        MsgSeqNum = int(Num)
        count[group] = MsgSeqNum

    print "Exiting Group %s... %s" % (group,datetime.datetime.now().strftime("%b %d %Y %X.%f"))

def join_group_lmax(group,args,event):
    global count
    (mcast_group,mcast_port) = group.split(":")
    sock = McastSocket(local_port=int(mcast_port),reuse=1)
    sock.mcast_add(mcast_group, args.interface)
    stime= datetime.datetime.now()
    print "Joining %s:%s at %s" % (mcast_group,mcast_port,stime.strftime("%b %d %Y %X.%f"))

    MsgSeqNum = 0
    while not event.isSet():
        sock.settimeout(30.0)
        msg,source = sock.recvfrom(1500)

        if len(msg) < 32:
            ''' hearbeat '''
            MsgSeqNum = MsgSeqNum + 1
            continue

        (Num,Time) = decode_lmax(msg)

        diff = int(Num) - MsgSeqNum
        if MsgSeqNum == 0:
                print "Decoding %s %s, Initial sequene number: %s" % (args.decode,group,int(Num))
        elif diff!=1:
                now =  datetime.datetime.now().strftime("%b %d %Y %X.%f")
                print "Gapped Detected %S, %s Packets, Sequence Numbers %s-%s at %s" %  (group,diff-1,MsgSeqNum+1,int(Num)-1,now)
        MsgSeqNum = int(Num)
        count[group] = MsgSeqNum

    print "Exiting Group %s... %s" % (group,datetime.datetime.now().strftime("%b %d %Y %X.%f"))

def main():
    parser = argparse.ArgumentParser(description='Subscribe and decode multicast for CME or LMAX')
    parser.add_argument('-g', '--group',action="append",required=True,help="Group(s) to join in IP:Port format, may be used more than once")
    parser.add_argument('-i','--interface',required=True,help="IP address of the Interface to join on")
    parser.add_argument('-d','--decode',required=True,choices=["lmax","cme"],help="LMAX or CME")
    parser.add_argument('-q',action="count",help="Do not print packet count")
    args = parser.parse_args()

    global estop, count
    count = {}

    ''' Allow Cntl-C to break out of loop '''
    signal.signal(signal.SIGINT, signal_handler)

    estop = threading.Event()
    threads = []
    for group in args.group:
        count[group] = 0
        if args.decode=="cme":
            t = threading.Thread(target=join_group_cme, args=(group,args,estop))
        elif args.decode=="lmax":
            t = threading.Thread(target=join_group_lmax, args=(group,args,estop))

        threads.append(t)
        t.start()

    while True:
        time.sleep(1)
        print "Sequence Number(S) at %s:" % (datetime.datetime.now().strftime("%b %d %Y %X.%f")),
        for c,v in count.items():
            print "%s: %s" % (c,v),
        print "\r",


if __name__ == '__main__':
    main()
