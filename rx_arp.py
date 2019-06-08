#!/usr/bin/env python3

#ARPChat, Charlie Camilleri 2019

from __future__ import print_function
from scapy.all import *
import time
import sys

direct=False

if len(sys.argv) > 1:
 if sys.argv[1] == "-d":
  print("Starting in DIRECT mode!")
  print(" ")
  direct=True

OUTFILE = "out.txt"

__version__ = "0.0.1"

buf = bytearray()

KEY = [0xDE,0xAD] # Encryption key!

def clear_buffer():
 buf = bytearray()

def handle_cmd(tip):

 if tip[0] == 0xFF and tip[1] == 0xFE:
  if direct == False:
   print("RX [",hex(tip[2]^KEY[0]),",",hex(tip[3]^KEY[1]),"]")
  else:
   print(str(chr(tip[2]^KEY[0]))+str(chr(tip[3]^KEY[1])),end='')

  buf.append(tip[2])
  buf.append(tip[3])
  return

 if tip[0] == 0xFF and tip[1] == 0xFF:
  if direct == False:
   print("Stream finished, saving")
   with open(OUTFILE, 'wb') as f:
    f.write(buf)
  else:
   pass
  clear_buffer()

 return

def handle_arp_packet(packet):

# print("=======PACKET=======")

 tip = bytes(packet[1])[24:28]

# print("TIP(A) = ",end='')
# for i in range(4):
#  print(str(int(tip[i]))+".",end='')
# print("")

# print("TIP(H) = ",tip.hex())

 handle_cmd(tip)

 return

if __name__ == "__main__":
    sniff(filter="arp", prn=handle_arp_packet)

