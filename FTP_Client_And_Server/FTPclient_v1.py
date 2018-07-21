#!usr/bin/python
#Code for a python client from class notes.
from socket import socket, AF_INET, SOCK_STREAM

def send(socket,msg):
    print "===>sending: " + msg
    socket.send(msg + "\r\n")
    recv = socket.recv(1024)
    print "<===receive: " + recv
    return recv

serverName = 'ftp.swfwmd.state.fl.us'
serverPort = 21
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
condition220 = True
message = clientSocket.recv(2048)
print message

while condition220:
    message = clientSocket.recv(2048)
    print message
    condition220 = message[0:6] != "220---"

message = send(clientSocket, "USER Anonymous")
message = send(clientSocket, "PASS lhern207@fiu.edu")
message = send(clientSocket, "TYPE A")
message = send(clientSocket, "PASV")
start = message.find("(")
end = message.find(")")
tuple = message[start+1:end].split(',')
port = int(tuple[4])*256 + int(tuple[5])

dataSocket = socket(AF_INET, SOCK_STREAM)
dataSocket.connect((serverName,port))
message = send(clientSocket, "LIST")
message = dataSocket.recv(2048)
print message
dataSocket.close()
message = clientSocket.recv(2048)
print message
message = send(clientSocket, "QUIT")
clientSocket.close()
