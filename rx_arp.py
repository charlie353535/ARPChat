#!/usr/bin/env python3

#ARPChat, Charlie Camilleri 2019

from __future__ import print_function
from scapy.all import *
import time
import sys
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import zlib

direct=False

aes_key = bytes([0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xA,0xB,0xC,0xD,0xE,0xF]) # NEW AES Key


PAIRCODE = bytearray([0,0])

if len(sys.argv) > 1:
 if sys.argv[1] == "-d":
  print("Starting in DIRECT mode!")
  print(" ")
  direct=True

if len(sys.argv) >2:
 if (sys.argv[2][0:2]) == "-c":
  PAIRCODE[0] = ord(sys.argv[2][2])
  PAIRCODE[1] = ord(sys.argv[2][3])

if len(sys.argv) > 3:
 if sys.argv[3][0:2] == "-k":
  k = bytearray(sys.argv[3].encode('ascii'))
  del k[0]
  del k[0]
  if len(k) != 16:
   print("ERROR, use a 16 byte key!")
   exit(1)
  aes_key = k

def checksum(data):
 data = bytearray(data)
 checksum = int(zlib.crc32(data) & 0xffffffff).to_bytes(4,byteorder='big')
 return checksum


OUTFILE = "out.txt"

__version__ = "0.0.1"

buf = bytearray([])

#KEY = [0xDE,0xAD] # OLD XOR Encryption key!

def clear_buffer():
 for i in range(len(buf)):
  del buf[0]

def decrypt_aes(data):
 data = bytearray(data)

 cipher = AES.new(aes_key, AES.MODE_ECB)
 plaintext = cipher.decrypt(data)

 return bytearray(plaintext)

def handle_cmd(tip):

 if tip[0] == 0xFF and tip[1] == 0xFE:
  if direct == False:
   print("RX [",hex(tip[2]^KEY[0]),",",hex(tip[3]^KEY[1]),"]")
  #else:
   # XOR legacy print(str(chr(tip[2]^KEY[0]))+str(chr(tip[3]^KEY[1])),end='')

  buf.append(tip[2])
  buf.append(tip[3])
  return

 if tip[0] == 0xFF and tip[1] == 0xFF:
  if direct == False:
   print("Stream finished, saving")
   with open(OUTFILE, 'wb') as f:
    f.write(decrypt_aes(buf))
  else:
   _checksum = bytearray(reversed(bytearray([buf.pop(len(buf)-1),buf.pop(len(buf)-1),buf.pop(len(buf)-1),buf.pop(len(buf)-1)])))
   if checksum(decrypt_aes(buf))!=_checksum: # Non-matching checksum, wrong key etc.
    clear_buffer()
    return
   for c in decrypt_aes(buf):
    print(chr(c),end='')
  clear_buffer()

 if tip[0] == 0xFF and tip[1] == 0xFD:
  if direct == True:
   if tip[2] == PAIRCODE[0] and tip[3] == PAIRCODE[1]:
    print("SIGINT recieved on TX process, exiting")
    exit(0)

  return


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


