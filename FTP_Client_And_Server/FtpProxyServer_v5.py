#!/usr/bin/python

#Fifth modification to class code for FTPServer.
#To be tested at http://ocelot.aul.fiu.edu:45681
#Additions: 
#Fixed some dynamic page formatting issues.
#Added a method to send timeout error to web browser.
#Provided error detection for both incorrect directory and filename.
#Code seems to work fine for small files and directories, however large files
#either take too long to transfer or just hang indefinitely. I can't figure
#out the motive. The server never acknowledges that it has sent the file.

from socket import socket, AF_INET, SOCK_STREAM, timeout
import time

def send(socket,msg):
    print "===>sending: " + msg
    socket.send(msg + "\r\n")
    recv = socket.recv(1024)
    print "<===receive: " + recv
    return recv

def dynamicHTML(socket, data):
    page = '''\
<!doctype html>
<html>
  <head>
    <b>Welcome
    <br>
    <br>
  </head>
  <body>
    <form method = "post" action = ""http://ocelot.aul.fiu.edu:45681"">
     <b>
     Enter file/directory name:<input type = "text" name = "filename" value = "">
     <br>
     <input type = "submit" value = "Submit">
    </form>
    <b>
      <br>
      <br>
      Enter . and submit to re-display the current directory.
      <br>
      Enter .. and submit to display the parent directory.
    <hr>
    <pre>
     {0}
    </pre>
  </body>
</html>
'''.format(data)

    headerline1 = "HTTP/1.1 200 OK\r\n"
    headerline2 = "Content-Length: " + str(len(page)) + "\r\n"
    headerline3 = "Content-Type: text/html\r\n\r\n"
    response = headerline1 + headerline2 + headerline3 + page
    socket.send(response)


def sendDataCommand(clientSocket, command):
    message = send(clientSocket, "PASV")
    start = message.find("(")
    end = message.find(")")
    tuple = message[start+1:end].split(',')
    port = int(tuple[4])*256 + int(tuple[5])
    dataSocket = socket(AF_INET, SOCK_STREAM)
    dataSocket.connect((serverName,port))

    message = send(clientSocket, command)
    code = message.split()[0]
    if code == "550":
        result = "Invalid File or Directory Name"
    else:
        result = ''
        while 1:
            data = dataSocket.recv(8192)
            result = result + data
            if len(data) < 8192:
                break

        message = clientSocket.recv(2048)
        print message
    dataSocket.close()
    return result

def ftpServerConnect(serverName, serverPort):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    condition220 = True
    message = clientSocket.recv(2048)
    print message

    #print all initial server information
    while condition220:
        message = clientSocket.recv(2048)
        print message
        condition220 = message[0:6] != "220---"

    #login, set transfer type to ascii
    send(clientSocket, "USER Anonymous")
    send(clientSocket, "PASS lhern207@fiu.edu")
    send(clientSocket, "TYPE A")
    return clientSocket

def sendError(socket, error):
    headerline1 = "HTTP/1.1" + error + "\r\n"
    headerline2 = "Content-Length = 0\r\n"
    headerline3 = "Connection: Closed\r\n\r\n"
    response = headerline1 + headerline2 + headerline3
    socket.send(response)


    
serverName = 'ftp.swfwmd.state.fl.us'
serverPort = 21
httpPort = 45681

clientSocket = ftpServerConnect(serverName, serverPort)

#set up socket to communicate with web form
httpSocket = socket(AF_INET, SOCK_STREAM)
httpSocket.bind(('', httpPort))
httpSocket.listen(1)

print "Interrupt with CTRL-C"

#Main server loop
while 1:
  try:
    print "Ready...Waiting for client connection..."
    #A connection has been made
    connectionSocket, addr = httpSocket.accept()
    connectionSocket.settimeout(200)
    #A flag to detect if the default page has already been provided
    #for this session. Subsequent GET requests will be ignored.
    default = 0
    
    #Loop to keep connection state, ends on timeout.
    #Program kills connection but server keeps running
    #and expecting other connections
    while 1:
        try:
            print "Ready to serve connected client...\n"
            httpMessage = ''
            while 1:
                data = connectionSocket.recv(4096)
                httpMessage = httpMessage + data
                if len(data) < 4096:
                    break
          
            method = httpMessage.split()[0]

            #Provide default page
            if method == "GET":
                if default == 0:
                    result = send(clientSocket, "PWD")
                    result += sendDataCommand(clientSocket, "LIST")
                    dynamicHTML(connectionSocket, result)
                    default = 1
                continue

            tokens = httpMessage.split("\r\n\r\n")
            querystring = tokens[1]
            fields = querystring.split("&")
            filename = (fields[0].split("="))[1]

            #Attempt to change directory    
            response = send(clientSocket, "CWD " + filename)
            status = response.split()[0]
    
            #If unsuccessful, retrieve file
            if status == "550":
                result = sendDataCommand(clientSocket, "RETR " + filename)
    
            #Otherwise print directory path and contents
            else:
                result = send(clientSocket, "PWD")
                result += sendDataCommand(clientSocket, "LIST")
        
            #Send result to web form
            dynamicHTML(connectionSocket, result)    
        except timeout:
            print "Client has timed out due to inactivity"
            print "Client Connection Closed\n"
            sendError(connectionSocket, "408 Request Timeout")
            connectionSocket.close()
            break
            
  except KeyboardInterrupt:
    message = send(clientSocket, "QUIT")
    clientSocket.close()
    httpSocket.close()
    break
