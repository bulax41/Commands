#!/usr/bin/env python
import argparse
from ftplib import FTP
import xml.etree.ElementTree
from StringIO import StringIO

parser = argparse.ArgumentParser(description='Parse the CME\'s config.xml file.  With no arguments it just prints out all channel ID\'s and labels')
parser.add_argument('-c', '--channel', type=int, help="Channel number to print out details")
args = parser.parse_args()
'''
  <channel id="310" label="CME Globex Equity Futures">
    <products>
      <product code="0ES">
        <group code="$E"/>
      </product>
      <product code="ES">
        <group code="ES"/>
      </product>
    </products>
   <connections>
    <connection id="310H2A">
      <type feed-type="H">Historical Replay</type>
      <protocol>TCP/IP</protocol>
      <host-ip>205.209.220.72</host-ip>
      <host-ip>205.209.222.72</host-ip>
      <port>10000</port>
      <feed>A</feed>
    </connection>
    <connection id="310IA">
      <type feed-type="I">Incremental</type>
      <protocol>UDP/IP</protocol>
      <ip>224.0.31.1</ip>
      <host-ip>205.209.223.70</host-ip>
      <host-ip>205.209.221.70</host-ip>
      <port>14310</port>
      <feed>A</feed>
    </connection>
    <connection id="310IB">
      <type feed-type="I">Incremental</type>
      <protocol>UDP/IP</protocol>
      <ip>224.0.32.1</ip>
      <host-ip>205.209.212.70</host-ip>
      <host-ip>205.209.211.70</host-ip>
      <port>15310</port>
      <feed>B</feed>
    </connection>
    <connection id="310NA">
      <type feed-type="N">Instrument Replay</type>
      <protocol>UDP/IP</protocol>
      <ip>224.0.31.43</ip>
      <host-ip>205.209.222.85</host-ip>
      <host-ip>205.209.222.73</host-ip>
      <port>14310</port>
      <feed>A</feed>
    </connection>
    <connection id="310NB">
      <type feed-type="N">Instrument Replay</type>
      <protocol>UDP/IP</protocol>
      <ip>224.0.32.43</ip>
      <host-ip>205.209.214.48</host-ip>
      <host-ip>205.209.213.48</host-ip>
      <port>15310</port>
      <feed>B</feed>
    </connection>
    <connection id="310SA">
      <type feed-type="S">Snapshot</type>
      <protocol>UDP/IP</protocol>
      <ip>224.0.31.22</ip>
      <host-ip>205.209.222.87</host-ip>
      <host-ip>205.209.222.77</host-ip>
      <port>14310</port>
      <feed>A</feed>
    </connection>
    <connection id="310SB">
      <type feed-type="S">Snapshot</type>
      <protocol>UDP/IP</protocol>
      <ip>224.0.32.22</ip>
      <host-ip>205.209.213.52</host-ip>
      <host-ip>205.209.214.52</host-ip>
      <port>15310</port>
      <feed>B</feed>
    </connection>
    <connection id="310SAMBO">
      <type feed-type="SMBO">Snapshot-MBO</type>
      <protocol>UDP/IP</protocol>
      <ip>233.72.75.1</ip>
      <host-ip>205.209.222.108</host-ip>
      <host-ip>205.209.222.109</host-ip>
      <port>23310</port>
      <feed>A</feed>
    </connection>
    <connection id="310SBMBO">
      <type feed-type="SMBO">Snapshot-MBO</type>
      <protocol>UDP/IP</protocol>
      <ip>233.72.75.64</ip>
      <host-ip>205.209.214.64</host-ip>
      <host-ip>205.209.213.64</host-ip>
      <port>22310</port>
      <feed>B</feed>
    </connection>
   </connections>
  </channel>
'''
cfile = StringIO()
ftp = FTP('ftp.cmegroup.com')
ftp.login()
ftp.retrbinary('RETR SBEFix/Production/Configuration/config.xml', cfile.write)

e = xml.etree.ElementTree.fromstring(cfile.getvalue())

if args.channel:
    for channel in e:
        if int(channel.attrib['id'])==args.channel:
            print "Channel ID: %s, Label: %s" % (channel.attrib['id'],channel.attrib['label'])
            for connections in channel.findall('connections'):
                for connection in connections.findall('connection'):
                    if connection.find('protocol').text=="UDP/IP":
                        hostip = "Sources: "
                        comma = ""
                        for host in connection.findall('host-ip'):
                            hostip += comma + host.text
                            comma = ","
                        print "\tFeed %s, Type %-20s %s:%s   %s" % \
                            (
                            connection.find('feed').text,
                            connection.find('type').text + ",",
                            connection.find('ip').text,
                            connection.find('port').text,
                            hostip
                            )

else:
    for channel in e:
        print "Channel %s, Label: %s" % (channel.attrib['id'],channel.attrib['label'])
