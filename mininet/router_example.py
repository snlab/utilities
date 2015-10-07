#!/usr/bin/python
"""
Router example
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class NetworkTopo( Topo ): 

	def build( self, **_opts):
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')
		s3 = self.addSwitch('s3')
		s4 = self.addSwitch('s4')
		h1 = self.addHost('h1',ip='10.0.1.2/24')
		h2 = self.addHost('h2',ip='10.0.1.3/24')
		h3 = self.addHost('h3',ip='10.0.2.2/24')
		self.addLink(s1,s2)
		self.addLink(s1,s3,intfName1='s1-eth2',params1={'ip':'10.0.1.1/24'})
		self.addLink(s2,s4,intfName1='s2-eth2',params1={'ip':'10.0.2.1/24'})
		self.addLink(h1,s3)
		self.addLink(h2,s3)
		self.addLink(h3,s4)

def run():
	topo = NetworkTopo()
	net = Mininet( topo=topo, controller = RemoteController('c1'))
	net.start()
	print net['h1'].cmd('route add default gw 10.0.1.1')
	print net['h2'].cmd('route add default gw 10.0.1.1')
	print net['h3'].cmd('route add default gw 10.0.2.1')
	CLI( net )
	net.stop()

if __name__ == '__main__':
	setLogLevel('info')
	run()
