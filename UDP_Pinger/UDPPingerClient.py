#!/usr/bin/python
#UDPPingerClient.py

from socket import socket, AF_INET, SOCK_DGRAM, timeout

serverName = 'localhost'
serverPort = 45678
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
message = raw_input('Input lowercase sentence: ')
clientSocket.sendto(message, (serverName, serverPort))
modifiedMessage = ''
address = ()
while 1:
    try:
        data, addr = clientSocket.recvfrom(2048)
        modifiedMessage = modifiedMessage + data
        if len(data) < 2048:
            address = address + addr
            break
    except timeout:
        print "Timeout"
        modifiedMessage = ''
        break

if modifiedMessage != '':
    print modifiedMessage, addr
clientSocket.close()
