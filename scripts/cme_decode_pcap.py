#!/usr/bin/env python
import dpkt
import argparse
import struct
import sys
import datetime



def main():
    parser = argparse.ArgumentParser(description='Read PCAP file, decode CME data and output message sequence gaps')
    parser.add_argument('-f','--file',help="PCAP File to read")
    args = parser.parse_args()

    with open(args.file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)

        Packets = 0
        Gaps = 0
        MsgSeqNum = 0
        for timestamp, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            (seqnum,pcktime) = struct.unpack_from(">IQ",ip.data[:5])
            diff = int(seqnum) - MsgSeqNum
            if MsgSeqNum == 0:
                print "Initial sequence number: %s" % int(seqnum)
            elif diff!=1:
                Gaps = Gaps + diff - 1
                now =  datetime.datetime.utcfromtimestamp(timestamp).strftime("%b %d %Y %X.%f")
                print "Gapped Detected, %s Packets, Sequence Numbers %s-%s at %s" %  (diff-1,MsgSeqNum+1,int(Num)-1,now)
            MsgSeqNum = int(seqnum)
            Packets = Packets + 1


    pcap.close()
    print "Ending Sequence number: %s, total packets %s" % (MsgSeqNum,Packets)


if __name__ == '__main__':
    main()
