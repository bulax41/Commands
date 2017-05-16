#!/bin/python
import socket
import struct
import sys
import signal
import time
import datetime
import argparse

class McastSocket(socket.socket):
  def __init__(self, local_port, reuse=False):
    socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    if(reuse):
      self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      if hasattr(socket, "SO_REUSEPORT"):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    self.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8388608)
    self.bind(('', local_port))
  def mcast_add(self, addr, iface):
    self.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(addr) + socket.inet_aton(iface))

def help(error=False):
   print
   print "Usage: %s {MulticastGroup}:{port} {interface_ip} {decoder}\n" % sys.argv[0]
   print
   print "Decoder:  Decode packets for sequence number and display gaps in packet sequence numbers"
   print "          It can be left blank and just a running total of received packets is desplayed"
   print
   print "          cme: decode SBEFix encoded packets from CME's Globex platform"
   print "               Expecting an Incremental channel as defined in the published produciton config.xml file"
   print "               ftp.cmegroup.com/SBEFix/Production/Configuration/config.xml "
   print
   print "          lmax: decode multicast data for LMAX Exchange multicast market data service"
   print "                Available groups appear to be: 233.162.5.64 - 233.162.5.69,   Port 16667 "
   print
   print
   sys.exit()

def parse_args():

   if len(sys.argv) == 3:
        options = sys.argv[1].split(":")
        options.append(sys.argv[2])
        options.append("")
        return (options)
   elif len(sys.argv) == 4:
        options = sys.argv[1].split(":")
        options.append(sys.argv[2])
        options.append(sys.argv[3])
        if sys.argv[3] != "cme"  and sys.argv[3] != "lmax":
                help()
        return (options)
   else:
        help()

def signal_handler(signal, frame):
        print
        print "Exiting... %s" % datetime.datetime.now().strftime("%b %d %Y %X.%f")
        sys.exit(0)

def decode_cme(msg):
   return  struct.unpack_from("IQ",msg)

def decode_lmax(msg):
   (sessionid,seqnum,msglength,msgtype,msgseqnum,timesec,timenanos) = struct.unpack_from("<IQHHQII",msg)
   pcktime = int(timesec) + int(timenanos)
   return (seqnum,pcktime)

def main():

   (mcast_group,mcast_port,intf,decode) = parse_args()

   signal.signal(signal.SIGINT, signal_handler)

   sock = McastSocket(local_port=int(mcast_port), reuse=1)
   sock.mcast_add(mcast_group, intf)

   stime= datetime.datetime.now()
   print "Joining %s:%s at %s" % (mcast_group,mcast_port,stime.strftime("%b %d %Y %X.%f"))

   count=0
   MsgSeqNum = 0
   while True:
        msg,source = sock.recvfrom(1500)
        count = count+1
        if decode != "":
                if decode == "cme":
                        (Num,Time) = decode_cme(msg)
                elif decode == "lmax":
                        if len(msg) < 32:
                                ''' hearbeat '''
                                MsgSeqNum = MsgSeqNum + 1
                                continue
                        (Num,Time) = decode_lmax(msg)

                diff = int(Num) - MsgSeqNum
                if MsgSeqNum == 0:
                        print "Decoding %s, Initial sequene number: %s" % (decode,int(Num))
                elif diff!=1:
                        now =  datetime.datetime.now().strftime("%b %d %Y %X.%f")
                        print "Gapped Detected, %s Packets, Sequence Numbers %s-%s at %s" %  (diff-1,MsgSeqNum+1,int(Num)-1,now)
                MsgSeqNum = int(Num)



        print "Packets Received: %s" % count ,
        print '\r',



if __name__ == '__main__':
    main()
