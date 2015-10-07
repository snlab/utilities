#!/usr/bin/python

"""
SDN topology of ysn_5.py
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class NetworkTopo( Topo ): 

	def build( self, **_opts):
		# subnet 10.1.1.0/24
		r1 = self.addSwitch('s6')
		s1 = self.addSwitch('s1')
		h1 = self.addHost('h1',ip='10.1.1.2/24', defaultRoute='10.1.1.1')
		h2 = self.addHost('h2',ip='10.1.1.3/24', defaultRoute='10.1.1.1')
		self.addLink(r1,s1,intfName1='s6-eth0',params1={'ip':'10.1.1.1/24'})
		self.addLink(h1, s1)
		self.addLink(h2, s1)
		# router 2
		r2 = self.addSwitch('s7')
		self.addLink(r1, r2, intfName1='s6-eth1',intfName2='s7-eth1',params1={'ip':'192.31.2.1/24'},params2={'ip':'192.32.2.8/24'})
		# subnet 10.1.2.0/24
		s2 = self.addSwitch('s2')
		s3 = self.addSwitch('s3')
		h3 = self.addHost('h3',ip='10.1.2.101/24', defaultRoute='10.1.2.10')
		h4 = self.addHost('h4',ip='10.1.2.102/24', defaultRoute='10.1.2.10')
		self.addLink(r2,s2,intfName1='s7-eth0',params1={'ip':'10.1.2.10/24'})
		self.addLink(s2,h3)
		self.addLink(s2,s3)
		self.addLink(s3,h4)
		#subnet 10.1.3.0/24
		s4 = self.addSwitch('s4')
		h5 = self.addHost('h5',ip='10.1.3.2/24', defaultRoute='10.1.3.1')
		h6 = self.addHost('h6',ip='10.1.3.3/24', defaultRoute='10.1.3.1')
		self.addLink(r2,s4,intfName1='s7-eth2',params1={'ip':'10.1.3.1/24'})
		self.addLink(s4,h5)
		self.addLink(s4,h6)
		#subnet 10.1.4.0/24
		s5 = self.addSwitch('s5')
		h7 = self.addHost('h7',ip='10.1.4.2/24', defaultRoute='10.1.4.1')
		h8 = self.addHost('h8',ip='10.1.4.3/24', defaultRoute='10.1.4.1')
		self.addLink(r2,s5,intfName1='s7-eth3',params1={'ip':'10.1.4.1/24'})
		self.addLink(s5,h7)
		self.addLink(s5,h8)

		self.addLink(h2,s5,intfName1='h2-eth1',params1={'ip':'10.1.4.4/24'})

def run():
	topo = NetworkTopo()
	net = Mininet( topo=topo, controller = RemoteController('c1'))
	net.start()
	print net['h1'].cmd('route add default gw 10.1.1.1')
	print net['h2'].cmd('route add default gw 10.1.1.1')
	print net['h3'].cmd('route add default gw 10.1.2.10')
	print net['h4'].cmd('route add default gw 10.1.2.10')            
	print net['h5'].cmd('route add default gw 10.1.3.1')
	print net['h6'].cmd('route add default gw 10.1.3.1')       
	print net['h7'].cmd('route add default gw 10.1.4.1')
	print net['h8'].cmd('route add default gw 10.1.4.1')
	CLI( net )
	net.stop()

if __name__ == '__main__':
	setLogLevel('info')
	run()
