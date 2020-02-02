## mininet+ryu for shortest path application
There are three main files there:

* create_topo.py: the python code used to implement customized network topology using Mininet's python API
* sp.py: the "shortest path" application using Ryu's python API
* MiniNAM.py + conf.config: [MiniNAM](https://www.ucc.ie/en/misl//research/software/mininam/) is based on mininet, and its usage is the same as mininet, but with an additional runtime interface.


Steps:

1. We can open a terminal to start controller process with the command below. The *--observe-links* should be added to discover the topology, otherwise no link information can be seen.
	
	```bash
	sudo ryu-manager sp.py --observe-links
	```

2. We can open another terminal with the command below to run MiniNAM to start Mininet and create a customized network. The * --controller = remote* parameter is used to connect the started controller process of Ryu.
	
	```bash
	sudo python MiniNAM.py --custom create_topo.py --topo mytopo,3 --controller=remote
	```
	
	![image.png](http://upload-images.jianshu.io/upload_images/3238358-6f0fef16646039e8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

3. We will have a network shown above, and we can test the "shortest path application" using hosts ping or iperf. For example,  let h1 ping h2 in the mininet and send 4 packets.
	
	```
	mininet>h1 ping -c 4 h2
	```
4. We can see that the path taken of the packet is h1-> s1-> s4-> s5-> s3-> h2, but not the shortest h1->s1-> s2-> s3-> h2. The reason is that the function *_packet_in_handler (self, ev)* in sp.py, the edge weight between switches is manually assigned, which is demonstrated in the figure below. In this case, the weight of the path h1-> s1-> s4-> s5-> s3-> h2 will be less than the h1->s1-> s2-> s3-> h2.

	![image.png](http://upload-images.jianshu.io/upload_images/3238358-0cddc94dfc1f914e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
	
