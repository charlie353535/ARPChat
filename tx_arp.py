#!/usr/bin/env python3

#ARPChat, Charlie Camilleri 2019

from scapy.all import *
import sys
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import zlib

aes_key = bytes([0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xA,0xB,0xC,0xD,0xE,0xF]) # Default AES Key

def encrypt_aes(data):
 data = bytearray(data)

 while (len(data)%16)!=0:
  data.append(0) # Pad out to 16 bytes

 cipher = AES.new(aes_key, AES.MODE_ECB)
 ciphertext = cipher.encrypt(data)

 return bytearray(ciphertext)

def decrypt_aes(data):
 data = bytearray(data)

 cipher = AES.new(aes_key, AES.MODE_ECB)
 plaintext = cipher.decrypt(data)

 return bytearray(plaintext)


# Legacy XOR key.
#KEY = [0xDE,0xAD] # Encryption key!

if (len(sys.argv) < 2):
 print("usage: ./tx_arp.py [ <filename> | -d ] [ -c ] [ <uname> ] [ -k ]")
 exit(1)

name="NONAME"

if len(sys.argv) == 3:
 name=sys.argv[2]

buf = bytearray()
direct=False

PAIRCODE = bytearray([0,0])

MAC_SRC = '70:10:6f:8f:03:00'  #'c4:9d:ed:2a:df:46'
IP_SRC = '0.0.0.0'

chat = False

if len(sys.argv) > 2:
 if sys.argv[2][0:2] == "-c":
  chat = True
  PAIRCODE[0] = ord(sys.argv[2][2])
  PAIRCODE[1] = ord(sys.argv[2][3])
  name = sys.argv[3]

if len(sys.argv) > 4:
 if sys.argv[4][0:2] == "-k":
  k = bytearray(sys.argv[4].encode('ascii'))
  del k[0]
  del k[0]
  if len(k) != 16:
   print("ERROR, use a 16 byte key!")
   exit(1)
  aes_key = k

if sys.argv[1] == "-d":
 print("Starting in DIRECT mode!")
 if name=="NONAME":
  name=input("Your Name (for -d chat mode): ")
 print("Just type your message and press [ENTER] to send it!")
 print("")
 direct=True
else:
 with open(sys.argv[1], 'rb') as f:
  buf = f.read()

if not direct:
 buf = bytearray(buf)
 length = len(buf)
 if (length%2)!=0:
  print("Too short, padding")
  buf.append(0)
  length=length+1

def checksum(data):
 data = bytearray(data)
 checksum = int(zlib.crc32(data) & 0xffffffff).to_bytes(4,byteorder='big')
 return checksum

def construct_ip(data):
 out=""
 for i in range(4):
  out = out+str(int(data[i]))
  if i != 3:
   out=out+"."
 return out

def sigint_handle(sig,frame):
 print("\u001b[0m",end='')
 print("SIGINT Triggered, exiting")
 if chat:
  dip = construct_ip([0xFF,0xFD,PAIRCODE[0],PAIRCODE[1]])
  sendp(Ether(src=MAC_SRC,dst='ff:ff:ff:ff:ff:ff') / ARP(op=1, psrc=IP_SRC, pdst=dip,hwsrc=MAC_SRC,hwdst='00:00:00:00:00:00') / Raw(load="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),verbose=0)
 sys.exit(0)

import signal
signal.signal(signal.SIGINT, sigint_handle)

buf = encrypt_aes(buf)

if not direct:
	print("\033[s\033[1;0H\u001b[41mTRANSMITTING...         ")
	for i in range(0,length,2):
		# Legacy XOR
		#dip = construct_ip([0xFF,0xFE,buf[i]^KEY[0],buf[i+1]^KEY[1]])

		# New AES
		dip = construct_ip([0xFF,0xFE,buf[i],buf[i+1]])
		print("\033[1;20H"+str(round((i/length)*100))+"%")
		sendp(Ether(src=MAC_SRC,dst='ff:ff:ff:ff:ff:ff') / ARP(op=1, psrc=IP_SRC, pdst=dip,hwsrc=MAC_SRC,hwdst='00:00:00:00:00:00') / Raw(load="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),verbose=0)

	dip = construct_ip([0xFF,0xFF,0x00,0x00])
	print("\033[1;0H\u001b[42mDONE.                   \033[u\033[1A\u001b[0m")
	sendp(Ether(src=MAC_SRC,dst='ff:ff:ff:ff:ff:ff') / ARP(op=1, psrc=IP_SRC, pdst=dip,hwsrc=MAC_SRC,hwdst='00:00:00:00:00:00') / Raw(load="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),verbose=0)

#MAC_SRC = '70:10:6f:8f:03:00'  #'c4:9d:ed:2a:df:46'
#IP_SRC = '0.0.0.0'

if direct:
 while True:
  buf = bytearray(str("["+name+"] "+input("=> ")+"\n").encode('ascii'))
  while (len(buf)%16)!=0:
   buf.append(0) # Pad out to 16 bytes
  _checksum = checksum(buf)
  buf = encrypt_aes(buf)
  buf.extend(_checksum)
  length = len(buf)
  if (length%2)!=0:
   buf.append(0)
   length=length+1

  print("\033[s\033[1;0H\u001b[41mTRANSMITTING...         ")

  for i in range(0,length,2):
   print("\033[1;20H"+str(round((i/length)*100))+"%")
   #Legacy XOR
   #dip = construct_ip([0xFF,0xFE,buf[i]^KEY[0],buf[i+1]^KEY[1]])

   dip = construct_ip([0xFF,0xFE,buf[i],buf[i+1]])
   sendp(Ether(src=MAC_SRC,dst='ff:ff:ff:ff:ff:ff') / ARP(op=1, psrc=IP_SRC, pdst=dip,hwsrc=MAC_SRC,hwdst='00:00:00:00:00:00')/ Raw(load="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),verbose=0)

  dip = construct_ip([0xFF,0xFF,0x00,0x00])
  sendp(Ether(src=MAC_SRC,dst='ff:ff:ff:ff:ff:ff') / ARP(op=1, psrc=IP_SRC, pdst=dip,hwsrc=MAC_SRC,hwdst='00:00:00:00:00:00') / Raw(load="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),verbose=0)

  print("\033[1;0H\u001b[42mDONE.                   \033[u\033[1A\u001b[0m")
