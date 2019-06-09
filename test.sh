#!/bin/bash

sudo pip install --pre scapy
sudo apt install -y tcpdump

sudo ./tx_arp.py README.md # Test send
