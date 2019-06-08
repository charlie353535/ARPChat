#!/bin/bash

echo "==ARPChat, Charlie Camilleri 2019=="

# check for and download scripts
if [ $(ls -al | grep -c "rx_arp.py") -lt 1 ]
	then
		echo "Downloading rx_arp.py"
		curl -L "https://raw.githubusercontent.com/Cvdcamilleri/ARPChat/master/rx_arp.py" -o rx_arp.py
		chmod 777 rx_arp.py
fi

if [ $(ls -al | grep -c "tx_arp.py") -lt 1 ]
        then
                echo "Downloading tx_arp.py"
		curl -L "https://raw.githubusercontent.com/Cvdcamilleri/ARPChat/master/tx_arp.py" -o tx_arp.py
		chmod 777 tx_arp.py
fi


#Check for python3
if [ $(dpkg-query -l python3 | grep python3 -c) -lt 1 ]
	then
		echo "PYTHON3 isn't installed! Installing now.."
		sudo apt install -y python3
fi

#Check for python3-pip
if [ $(dpkg-query -l python3-pip | grep python3-pip -c) -lt 1 ]
        then
                echo "PYTHON3 isn't installed! Installing now.."
                sudo apt install -y python3-pip
fi


#Check scapy
if [ $(pip3 list 2> /dev/null| grep -c scapy) -lt 1 ]
	then
		echo "PYTHON-SCAPY isn't installed! Installing now.."
		sudo apt install -y tcpdump
		sudo pip3 install --pre scapy
fi

echo -n "Your name (One Word): "
read name
echo

export NAME="$name"

echo "split" >> screentemp
echo "screen /bin/bash -c 'sudo ./rx_arp.py -d'" >> screentemp
echo "focus" >> screentemp
echo "screen /bin/bash -c 'sudo ./tx_arp.py -d $NAME'" >> screentemp
echo 'caption string "ARPChat, Charlie Camilleri 2019"' >> screentemp

screen -c screentemp

rm screentemp
