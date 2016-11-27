for x in {244..257}
do
   for y in {1..254}
   do
   iptables -N BROKER-185.96.$x.$y
   done
done

iptables -N BROKERNET-UK
iptables -N BROKERNET-US
iptables -N BROKERNET-HK
iptables -N BROKERNET-JP

for i in {1..254}; 
do 
iptables -A BROKERNET-UK  -d 185.96.244.$i -m hashlimit --hashlimit-upto 8mb/s --hashlimit-mode dstip --hashlimit-name tc-185.96.244.$i  -j BROKER-185.96.244.$i 
iptables -A BROKERNET-UK  -d 185.96.244.$i -m recent --name broker-185.96.244.$i --rcheck --seconds 604800 -j BROKER-185.96.244.$i 
done
for i in {1..254}; 
do 
iptables -A BROKERNET-US  -d 185.96.245.$i -m hashlimit --hashlimit-upto 8mb/s --hashlimit-mode dstip --hashlimit-name tc-185.96.245.$i  -j BROKER-185.96.245.$i 
iptables -A BROKERNET-US  -d 185.96.245.$i -m recent --name broker-185.96.245.$i --rcheck --seconds 604800 -j BROKER-185.96.245.$i    
done
for i in {1..254}; 
do 
iptables -A BROKERNET-JP  -d 185.96.246.$i -m hashlimit --hashlimit-upto 8mb/s --hashlimit-mode dstip --hashlimit-name tc-185.96.246.$i  -j BROKER-185.96.246.$i 
iptables -A BROKERNET-JP  -d 185.96.246.$i -m recent --name broker-185.96.246.$i --rcheck --seconds 604800 -j BROKER-185.96.246.$i 
done
for i in {1..254}; 
do 
iptables -A BROKERNET-HK  -d 185.96.247.$i -m hashlimit --hashlimit-upto 8mb/s --hashlimit-mode dstip --hashlimit-name tc-185.96.247.$i  -j BROKER-185.96.247.$i;
iptables -A BROKERNET-HK  -d 185.96.247.$i -m recent --name broker-185.96.247.$i --rcheck --seconds 604800 -j BROKER-185.96.247.$i
done
