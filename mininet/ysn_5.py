#!/usr/bin/python

"""
linuxrouter.py: Example network with Linux IP router

This example converts a Node into a router using IP forwarding
already built into Linux.

The topology contains

MX-router (r1) with two IP subnets:
 - 130.132.11.0/24 (interface r1-eth1 IP: 130.132.11.1)
 - 192.31.2.0/24 (interface r1-eth2 IP: 192.31.2.1)

 - h1 (IP: 130.132.11.100) connected to r1-eth1
 - r2 (IP: 192.32.2.8) connected to r1-eth2

KBT (r2) with two IP subnets:
 - 192.31.2.0/24 (interface r2-eth1 IP: 192.31.2.8)
Assuming KBT has a port on vlan200 and vlan200 is 172.28.28.0/24
 - 172.28.28.0/8 (interface r2-eth2 IP: 172.28.28.10)

 - r1 (IP: 192.31.2.1) connected to r2-eth1
 - s1 (IP: 172.28.28.1) connected to r2-eth2

300G-Router (s1):
Acting as a legacy L2 switch on vlan 172.28.28.0/24
 - r2 (IP: 172.28.28.10) connected to s1-eth1
 - h3 (IP: 172.28.28.101) connected to s1-eth2
 - s2 connected to s1-eth3

WC-Switch (s2): 
Acting as a Legacy L2 switch on vlan 172.28.28.0/24
 - s1 connected to s2-eth1
 - h4 connected to s2-eth2


 Routing entries can be added to the routing tables of the
 hosts or router using the "ip route add" or "route add" command.
 See the man pages for more details.

"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A simple topology of a router with three subnets (one host in each)."

    def build( self, **_opts ):
        r1 = self.addNode( 'r1', cls=LinuxRouter, ip='10.1.1.1/24')
        # TODO: Rename this to s1
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
        self.addLink(r1, s1, intfName1='r1-eth1', params1={'ip': '10.1.1.1/24'})
        h1 = self.addHost( 'h1', ip='10.1.1.2/24', defaultRoute='via 10.1.1.1' )
        h2 = self.addHost( 'h2', ip='10.1.1.3/24', defaultRoute='via 10.1.1.1' )
        self.addLink( h1, s1)
        self.addLink( h2, s1)        

        # router2
        r2 = self.addNode( 'r2', cls=LinuxRouter, ip='192.32.2.8/24' )
        self.addLink( r1, r2, intfName1='r1-eth2', intfName2='r2-eth1', params1={'ip' : '192.31.2.1/24'}, params2={'ip' : '192.32.2.8/24'})

        # subnet 10.1.2.0/24
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')
        self.addLink(r2, s2, intfName1='r2-eth2', params1={'ip': '10.1.2.10/24'})        
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch, failMode='standalone')
        h3 = self.addHost('h3', ip='10.1.2.101/24', defaultRoute='via 10.1.2.10')
        h4 = self.addHost('h4', ip='10.1.2.102/24', defaultRoute='via 10.1.2.10')
        self.addLink(s2, h3)
        self.addLink(s2, s3)
        self.addLink(s3, h4)

        # subnet 10.1.3.0/24
        s4 = self.addSwitch('s4', cls=OVSKernelSwitch, failMode='standalone')
        self.addLink(r2, s4, intfName1='r2-eth3', params1={'ip': '10.1.3.1/24'})        
        h5 = self.addHost('h5', ip='10.1.3.2/24', defaultRoute='via 10.1.3.1')
        h6 = self.addHost('h6', ip='10.1.3.3/24', defaultRoute='via 10.1.3.1')
        self.addLink(s4, h5)
        self.addLink(s4, h6)        

        # subnet 10.1.4.0/24
        s5 = self.addSwitch('s5', cls=OVSKernelSwitch, failMode='standalone')
        self.addLink(r2, s5, intfName1='r2-eth4', params1={'ip': '10.1.4.1/24'})        
        h7 = self.addHost('h7', ip='10.1.4.2/24', defaultRoute='via 10.1.4.1')
        h8 = self.addHost('h8', ip='10.1.4.3/24', defaultRoute='via 10.1.4.1')
        self.addLink(s5, h7)
        self.addLink(s5, h8)        

        self.addLink(s5, h2, params2={'ip':'10.1.4.4/24'})

        # h2 ip route del 10.1.3.0/24 via 10.1.4.1
        

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo, controller=None )  # no controller needed
    net.start()
    print net['r1'].cmd('ip route add 192.32.2.0/24 dev r1-eth2')
    print net['r1'].cmd('ip route add 10.1.2.0/24 via 192.32.2.8')
    print net['r1'].cmd('ip route add 10.1.3.0/24 via 192.32.2.8')
    print net['r1'].cmd('ip route add 10.1.4.0/24 via 192.32.2.8')            
    print net['r2'].cmd('ip route add 192.31.2.0/24 dev r2-eth1')
    print net['r2'].cmd('ip route add 10.1.1.0/24 via 192.31.2.1')

    net['h2'].cmd('sysctl net.ipv4.ip_forward=1')
    net['h2'].cmd('echo 0 > /proc/sys/net/ipv4/conf/default/rp_filter')
    net['h2'].cmd('echo 0 > /proc/sys/net/ipv4/conf/all/rp_filter')
    net['h2'].cmd('echo 0 > /proc/sys/net/ipv4/conf/h2-eth0/rp_filter')
    net['h2'].cmd('echo 0 > /proc/sys/net/ipv4/conf/h2-eth1/rp_filter')                

    
    info( '*** Routing Table on MX-104\n' )
    print net[ 'r1' ].cmd( 'route' )
    info( '*** Routing Table on KBT\n' )
    print net[ 'r2' ].cmd( 'route' )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
