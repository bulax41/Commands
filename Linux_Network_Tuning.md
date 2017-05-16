kernel



1. Driver NIC ring buffer sizing and tuning.  Depends on NIC type

  ethtool -S ethX     For hardware drops, due to ring buffer overflow
  ethtool -c ethX     ring buffer size


2. Kernel is notitifed to read packets from ring buffer using a hard interupt from NIC Driver.

  Check interupts /proc/interupts.
  Use service irqbalance to balance out NIC ingress/egress queues over all CPU's.

3. SoftIRQ's are used to drain the ring buffer.

  They can be seeing as a kernel process with "ps" command.  ksoftirqd/cpu-number
  Check that not CPU bound i.e. 100%

  /proc/softirqs
  /proc/net/softnet_stat   (Any column besides 1, increase net.core.netdev_budget, the number is messages read per read)
      Column 1 is the cpu-number
      Column 2 is the number of frames dropped due to netdev_max_backlog
      Column 3 is the number of time ksoftirqd ran out of netdev_budget   or CPU time.


Application:

4. UDP:  
    check errors in netstat -su
    Kernel: Set net.core.rmem_max=67108864, net.ipv4.udp_mem="262144 327680 393216"

    App: Set socket receive buffer size:  setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8388608)
