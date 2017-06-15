#!/usr/bin/env  python
import socket
import struct
import sys
import signal
import time
import datetime
import argparse
from mcast_listen import *

def decode_cme(msg):
   return  struct.unpack_from("IQ",msg)

def decode_lmax(msg):
   (sessionid,seqnum,msglength,msgtype,msgseqnum,timesec,timenanos) = struct.unpack_from("<IQHHQII",msg)
   pcktime = int(timesec) + int(timenanos)
   return (seqnum,pcktime)


def main():
    parser = argparse.ArgumentParser(description='Subscribe and decode multicast for CME or LMAX')
    parser.add_argument('-g', '--group',required=True,help="Group(s) to join in IP:Port format, may be used more than once")
    parser.add_argument('-i','--interface',required=True,help="IP address of the Interface to join on")
    parser.add_argument('-d','--decode',required=True,choices=["lmax","cme"],help="LMAX or CME")
    args = parser.parse_args()

    (mcast_group,mcast_port) = args.group.split(":")

    signal.signal(signal.SIGINT, signal_handler)

    sock = McastSocket(local_port=int(mcast_port), reuse=1)
    sock.mcast_add(mcast_group, args.interface)

    stime= datetime.datetime.now()
    print "Joining %s:%s at %s" % (mcast_group,mcast_port,stime.strftime("%b %d %Y %X.%f"))

    count=0
    MsgSeqNum = 0
    while True:
        msg,source = sock.recvfrom(1500)
        count = count+1

        if args.decode == "cme":
                (Num,Time) = decode_cme(msg)
        elif args.decode == "lmax":
                if len(msg) < 32:
                    ''' hearbeat '''
                    MsgSeqNum = MsgSeqNum + 1
                    continue
                (Num,Time) = decode_lmax(msg)

        diff = int(Num) - MsgSeqNum
        if MsgSeqNum == 0:
                print "Decoding %s, Initial sequene number: %s" % (args.decode,int(Num))
        elif diff!=1:
                now =  datetime.datetime.now().strftime("%b %d %Y %X.%f")
                print "Gapped Detected, %s Packets, Sequence Numbers %s-%s at %s" %  (diff-1,MsgSeqNum+1,int(Num)-1,now)
        MsgSeqNum = int(Num)

        print "Packets Received: %s" % count ,
        print '\r',




if __name__ == '__main__':
    main()
