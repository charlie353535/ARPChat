#!/bin/bash

sudo pip3 install --pre scapy
sudo apt install -y tcpdump

sudo ./tx_arp.py README.md # Test send
