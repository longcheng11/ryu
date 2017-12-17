## mininet+ryu下实现最短路径应用
shortest_path\_app/下的重要文件：

* create_topo.py：使用mininet的python API实现的自定义拓扑python代码
* sp.py：使用ryu的python API实现的“最短路径”应用
* MiniNAM.py+conf.config：MiniNAM就是在mininet的基础上，增加了运行时的界面，用法和mininet没区别

使用步骤：

1. 打开terminal，先运行ryu控制器进程，启动“最短路径”的应用
	
	```bash
	cd shortest_path_app/
	sudo ryu-manager sp.py --observe-links
	```
	其中的`--observe-links`必须要加：自动下发LLDP，用于拓扑发现，否则看不到链路信息

2. 再打开另一个terminal，运行MiniNAM以启动mininet，创建自定义的网络。使用`--controller=remote`参数连接上一步启动的ryu的控制器进程
	
	```bash
	cd shortest_path_app/
	# 可以把python MiniNAM.py替换成mn，因为MiniNAM.py只是mininet加个界面
	sudo python MiniNAM.py --custom create_topo.py --topo mytopo,3 --controller=remote
	```
	创建完成后如下图（通过手工拖拽，重新布局了），MiniNAM这货有一点不好的就是各个节点是随机布局，比较乱，要手动拽，比较烦。布局的代码在`def createNodes(self)`函数中，希望作者有空改一下，orz...
	
	![image.png](http://upload-images.jianshu.io/upload_images/3238358-6f0fef16646039e8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

3. 在mininet中，host互相ping或iperf发流，测试“最短路径应用”。在mininet窗口下让`h1 ping h2`，发送4个包
	
	```
	mininet>h1 ping -c 4 h2
	```
	可以看到包走的路径是`h1->s1->s4->s5->s3->h2`，为什么不走跳数更少的s1->s2->s3呢？

	因为在sp.py的`_packet_in_handler(self, ev)`函数中，大约170行左右，我写死了交换机间的边权。在162行，其它节点间的边权为0。
	
	带权图如下：
	
	![image.png](http://upload-images.jianshu.io/upload_images/3238358-0cddc94dfc1f914e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
	
	像我这样强制指定链路的边权是不合理的，可以通过某些手段测得链路的实际物理值：带宽、时延等。
	
	本ryu应用计算的是单源最短路，使用的是networkx提供的nx.shortest_path函数（sp.py的183行），读者可以换成其它的算法，例如多路径算法floyd，实现multipath。如果知道链路的带宽，还可以运行带宽相关的算法，比如实现负载均衡类型的应用。
	
* 备注1：这个拓扑图有环，arp我也没做什么处理。没出现风暴是因为网络小，在风暴来临之前就获知了h2的mac地址。。。后来我用wireshark抓包看了下，是出现了好多次无用arp，像我说的那样，网络小，在风暴来临前已经获知mac地址了。如果拓扑图大的话一定要使用生成树协议。。。
	
* 备注2：其实整体过程并不是很难理解，在h1使用arp协议获知h2的mac地址之后，h1发出icmp ping包，s1不知道怎么处理，让控制器c0做决定，然后c0掐指一算，最短路径是1-4-5-3，让s1发给s4，s4也不知道怎么处理，还发给c0，c0还要算一次最短路，让s4发给s5，如此下去，因此要调用多次最短路径。不过也就最开始这样，等以后多发几次包，交换机流表项都配置好后，以后就不用问控制器了，交换机就知道该送到哪个交换机了。不过如果链路的权重变化了，那就要通知控制器，重新计算最短路，这样就麻烦了。。。之前的流表项要删，控制器配置新的流表项。具体怎么实现“权重改变，通知控制器”我也在想该怎么实现。。。

## mininet简介
[mininet](http://mininet.org/)是一个轻量的进程级别的网络模拟器，[一共四种安装方法可以选择](http://mininet.org/download/)，推荐前两种：[直接下载官方镜像](http://mininet.org/download/#option-1-mininet-vm-installation-easy-recommended)或者[本地安装](http://mininet.org/download/#option-2-native-installation-from-source)。

命令行启动mininet：

```bash
# 先测试是否安装好，显示版本
mn --version

# 启动命令：不加任何参数的话，默认创建了一个小网络：1个控制器+1个交换机+2个host
sudo mn
开启后可以使用ping测试host的互通
> h1 ping h2

# 启动命令升级版：自定义拓扑，tree形，深度为2，分叉为3，如下图
sudo mn --topo=tree,depth=2,fanout=3
```
![](http://upload-images.jianshu.io/upload_images/3238358-cc5aba6c7e8213a5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/685)

mininet以python语言实现，可以像上面那样通过mn命令启动，也可以编写python程序调用api实现命令行的所用功能。`create_topo.py`就是通过api实现的自定义拓扑。

```bash
sudo mn --custom create_topo.py --topo mytopo,3
```

另外，在最新的Mininet2.2.0内置了一个mininet可视化工具miniedit，位于mininet/mininet/examples目录下的miniedit.py脚本，执行脚本后将显示Mininet的可视化界面，在界面上可进行自定义拓扑和自定义设置。使用图形界面设置好拓扑后，可以将其保存为python脚本，以后直接运行python脚本即可重现拓扑。


## MiniNAM简介
[MiniNAM](https://github.com/uccmisl/MiniNAM) = mininet + 动态可视化

mininet自带的可视化miniedit只是静态地创建网络的可视化。MiniNAM能够提供包转发的动态可视化，[论文链接](http://ieeexplore.ieee.org/document/7899417/)，[MiniNAM工程自带的三个应用：NAT、Routing、LoadBalancer的视频链接](https://www.youtube.com/watch?v=np6H75gNzmA&list=PLkflhn-Dnb66Ca3a3jdu-sSaFXGb--7po)。



## ryu控制器
[RYU控制器](https://osrg.github.io/ryu/)是日本NTT公司负责研发的一款开源的SDN/OpenFlow控制器，这个控制器是取名于日本的‘flow’的意思，所以叫RYU，RYU控制器完全有python语言编写，和POX类似。RYU控制器现在支持到OpenFlow版本的1.0，1.2，1.3，1.4版本，同时支持与OpenStack结合使用，应用 于云计算领域。RYU采用Apache Licence开源协议标准。

[github源码地址。](https://github.com/osrg/ryu)
自带的应用都放置在ryu/app文件夹下。
这样运行应用：

```bash
sudo ryu-manager yourapp.py
```
