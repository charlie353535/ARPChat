#!/bin/bash

sudo apt install python3 python3-pip -y

sudo pip3 install --pre scapy
sudo apt install -y tcpdump

sudo ./tx_arp.py README.md # Test send
