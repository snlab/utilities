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
from mininet.node import Node, Controller, RemoteController, OVSKernelSwitch
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
        router = self.addNode( 'r1', cls=LinuxRouter, ip='130.132.11.9/24')
        h1 = self.addHost( 'h1', ip='130.132.11.100/24',
                           defaultRoute='via 130.132.11.9' )
        self.addLink( h1, router, intfName2='r1-eth1',
                      params2={ 'ip' : '130.132.11.9/24' } )
        
	router2 = self.addNode( 'r2', cls=LinuxRouter, ip='192.32.2.8/24' )
        #h2 = self.addHost( 'h2', ip='172.28.28.100/24',
        #                   defaultRoute='via 172.28.28.10' )

	self.addLink( router, router2, intfName1='r1-eth2', intfName2='r2-eth1', params1={'ip' : '192.31.2.1/24'}, params2={'ip' : '192.32.2.8/24'})

        #self.addLink( h2, router2, intfName2='r2-eth2',
        #              params2={ 'ip' : '172.28.28.10/24' } )

	switch1 = self.addSwitch('s1')
	switch2 = self.addSwitch('s2')
	h3 = self.addHost('h3', ip='172.28.28.101/24', defaultRoute='via 172.28.28.10')
	h4 = self.addHost('h4', ip='172.28.28.102/24', defaultRoute='via 172.28.28.10')
	
	self.addLink(router2, switch1, intfName1='r2-eth2', params1={'ip': '172.28.28.10/24'})
	self.addLink(switch1, h3)
	self.addLink(switch1, switch2)
	self.addLink(switch2, h4)


def run():
    "Test linux router"
    topo = NetworkTopo()


    c0 = RemoteController('c0')
    net = Mininet( topo=topo, controller=c0)  # no controller needed
    net.start()
    print net['r1'].cmd('ip route add 192.32.2.0/24 dev r1-eth2')
    print net['r2'].cmd('ip route add 192.31.2.0/24 dev r2-eth1')
    print net['r1'].cmd('ip route add 172.28.28.0/24 via 192.32.2.8')
    print net['r2'].cmd('ip route add 130.132.11.0/24 via 192.31.2.1')
    info( '*** Routing Table on MX-104\n' )
    print net[ 'r1' ].cmd( 'route' )
    info( '*** Routing Table on KBT\n' )
    print net[ 'r2' ].cmd( 'route' )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
