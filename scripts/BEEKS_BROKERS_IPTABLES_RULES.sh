#!/bin/bash

LIST="185.96.244 185.96.245 185.96.246 185.96.247 103.73.124"

for x in $LIST
do
   echo "Creating NET and IP Chains: $x"
   iptables -N FILTER-NET-$x
   for y in {0..255}
   do
   iptables -N FILTER-IP-$x.$y
   iptables -A FILTER-IP-$x.$y -j DROP
   done

done

echo "Done with chains"

for net in $LIST
do
	echo "Creating filter rules for $net"

	for ip in {0..255}; 
	do 

	iptables -A FILTER-NET-$net  -d $net.$ip -m hashlimit --hashlimit-upto 100mb/s --hashlimit-mode dstip --hashlimit-name tc-$net.$ip  -j FILTER-IP-$net.$ip
	iptables -A FILTER-NET-$net  -d $net.$ip -m recent --name filter-$net.$ip --rcheck --seconds 604800 -j FILTER-IP-$net.$ip 

	done
done
