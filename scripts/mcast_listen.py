#!/bin/python
import socket
import struct
import sys
import signal
import time
import datetime
import argparse
import threading

class McastSocket(socket.socket):
  def __init__(self, local_port='', reuse=False):
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




def signal_handler(signal, frame):
        print
        print "Exiting... %s" % datetime.datetime.now().strftime("%b %d %Y %X.%f")
        estop.set()
        sys.exit(0)

def join_group(group,args,event):
    (mcast_group,mcast_port) = group.split(":")
    sock = McastSocket(local_port=int(mcast_port),reuse=1)
    sock.mcast_add(mcast_group, args.interface)
    stime= datetime.datetime.now()
    print "Joining %s:%s at %s" % (mcast_group,mcast_port,stime.strftime("%b %d %Y %X.%f"))
    count=0
    MsgSeqNum = 0
    while not event.isSet():
        msg,source = sock.recvfrom(1500)
        count = count+1
        if not args.quiet:
            print "Packets Received: %s" % count ,
            print '\r',




def main():
    parser = argparse.ArgumentParser(description='Subscribe and decode multicast for CME or LMAX')
    parser.add_argument('-g', '--group',action="append",required=True,help="Group to join in IP:Port format, may be used more than once")
    parser.add_argument('-i','--interface',required=True,help="IP address of the Interface to join on")
    parser.add_argument('-q','--quiet',action="count",help="Do not print packet count")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    global estop
    estop = threading.Event()
    threads = []
    for group in args.group:
        t = threading.Thread(target=join_group, args=(group,args,estop))
        threads.append(t)
        t.start()

    time.sleep(10)
    estop.set()



if __name__ == '__main__':
    main()
