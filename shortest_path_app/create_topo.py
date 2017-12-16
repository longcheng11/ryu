#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


class mytopo(Topo):
    def __init__(self, n=2, **opts):
        Topo.__init__(self, **opts)

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        s = []
        for i in range(6):
            switch = self.addSwitch('s%s' % i)
            s.append(switch)
        # print s

        self.addLink(h1, s[1])
        self.addLink(h2, s[3])

        self.addLink(s[1], s[2])
        self.addLink(s[2], s[3])

        self.addLink(s[1], s[4])
        self.addLink(s[4], s[5])
        self.addLink(s[5], s[3])

class SingleSwitch(Topo):
    "Single switch connected to n hosts."

    def __init__(self, n=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)

            # linkopts = dict(bw=10, delay='5ms', loss=10, max_queue_size=1000, use_htb=True)
            # (or you can use brace syntax: linkopts = {'bw':10, 'delay':'5ms', ... } )
            # self.addLink(node1, node2, **linkopts)


def simpleTest():
    "Create and test a simple network"
    topo = SingleSwitch(n=4)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.stop()


topos = {'SingleSwitch': SingleSwitch, 'mytopo':mytopo }
tests = {'mytest': simpleTest}

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
