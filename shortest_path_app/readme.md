mn演示
1. sudo mn	h1 ping h2
2. mininet api
2. miniedit

MiniNAM演示
1. sudo python mininet/MiniNAM.py


ryu演示 + mininet + shortestpath
1.
sudo ryu-manager mininet/sp.py --observe-links
sudo python mininet/MiniNAM.py --custom mininet/create_topo.py --topo mytopo,3  --controller=remote
