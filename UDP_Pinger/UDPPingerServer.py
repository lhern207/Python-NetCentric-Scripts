#UDPPingerServer.py
#!/usr/bin/python

import random
from socket import socket, SOCK_DGRAM, AF_INET

#Create a UDP socket 
#Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('', 45678))
print "Waiting for connections"
while True:
    rand = random.randint(0,10)
    # Receive the client packet along with the address it is coming from
    message = ''
    while 1:
        data, address = serverSocket.recvfrom(2048)
        message = message + data
        if len(data) < 2048:
            break

    # Capitalize the message from the client
    print message, address
    message = message.upper()

    if rand < 4:
        print "Packet loss simulated"
        continue
    serverSocket.sendto(message, address)
serverSocket.close()

