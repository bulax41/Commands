#!/bin/python
import socket
import struct
import sys

class McastSocket(socket.socket):
  def __init__(self, local_port, reuse=False):
    socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    if(reuse):
      self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      if hasattr(socket, "SO_REUSEPORT"):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    self.bind(('', local_port))
  def mcast_add(self, addr, iface):
    self.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(addr) + socket.inet_aton(iface))

def help(error=False):
   print "Usage: %s {MulticastGroup}:{port} {interface_ip}\n" % sys.argv[0] 

def parse_args():
   if len(sys.argv) != 3:
        help()  
        sys.exit()

   options = sys.argv[1].split(":")
   options.append(sys.argv[2])
   return (options)

def main():

   (mcast_group,mcast_port,intf) = parse_args()
   print "%s %s %s" % (mcast_group,mcast_port,intf)

   #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
   #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   #sock.bind((mcast_group, int(mcast_port))) 
   #mreq = struct.pack("4sl", socket.inet_aton(mcast_group), socket.inet_aton(intf))

   #sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
   sock = McastSocket(local_port=int(mcast_port), reuse=1)
   sock.mcast_add(mcast_group, intf)

   while True:
        print sock.recv(1024)

if __name__ == '__main__':
    main()
