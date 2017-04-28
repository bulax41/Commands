#!/bin/bash
NETS="38.76.16 38.76.17 192.81.110 208.78.38 192.81.111"

# Delete any existing root class:
iptables -F FORWARD

if [ "x$1" = "xstop" ]
then
  exit
fi

for i in $NETS;
do
  iptables -A FORWARD -m hashlimit --hashlimit-mode dstip --hashlimit-above 62.5mb/s --hashlimit-dstmask 32 --hashlimit-name tc-$i --hashlimit-burst 100mb -d $i.0/24 -j DROP
done




iptables -A FORWARD -d 185.96.244.0/24 -j FILTER-NET-185.96.244
iptables -A FORWARD -d 185.96.245.0/24 -j FILTER-NET-185.96.245
iptables -A FORWARD -d 185.96.246.0/24 -j FILTER-NET-185.96.246
iptables -A FORWARD -d 185.96.247.0/24 -j FILTER-NET-185.96.247
iptables -A FORWARD -d 103.73.124.0/24 -j FILTER-NET-103.73.124
