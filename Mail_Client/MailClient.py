#!usr/bin/python
#Mail client that receives mail fields from an HTML form and forwards the
#contents to fiu's SMTP server, which sends the email to the proper destination.
import socket
import time

def send_recv(socket, msg, code):
    if msg != None:
        print "Sending==> ", msg
        socket.send(msg + '\r\n')

    recv = socket.recv(1024)
    print "<==Received:\n", recv
    if recv[:3]!=code:
        print '%s reply not received from server.' % code
    return recv

def send(socket, msg):
    print "Sending ==> ", msg
    socket.send(msg + '\r\n')

def sendHttpResponse(connectionSocket):
    headerline1 = "HTTP/1.1 200 OK\r\n"
    message = "Email has been successfully sent!"
    headerline2 = "Content-Length: " + str(len(message)) + "\r\n\r\n"

    response = headerline1 + headerline2 + message
    connectionSocket.send(response)


httpPort = 45680
serverName = 'smtp.cis.fiu.edu'
serverPort = 25

httpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
httpSocket.bind(('', httpPort))
httpSocket.listen(1)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

print "Interrupt with CTRL-C"

while 1:
    try:
        print "Ready to serve..."

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))

        connectionSocket, addr = httpSocket.accept()
        message = ''
        while 1:
            data = connectionSocket.recv(4096)
            message = message + data
            if len(data) < 4096:
                break
        
        tokens = message.split("\r\n\r\n")
        querystring = tokens[1]
        fields = querystring.split("&")
        fromValue = (fields[0].split("="))[1]
        toValue = (fields[1].split("="))[1]
        subjectValue = (fields[2].split("="))[1]
        mailMessage = (fields[3].split("="))[1]
        
        clientName = "Client Lester"

        userName = fromValue.split("%40")[0]
        userServer = fromValue.split("%40")[1]
        toName = toValue.split("%40")[0]
        toServer = toValue.split("%40")[1]

        messageTokens = mailMessage.split("+")
        mailMessage = ''
        for token in messageTokens:
            mailMessage = mailMessage + token + " "

        recv=send_recv(clientSocket, None, '220')
        #Send HELO command and print server response.
        heloCommand='EHLO %s' % clientName
        recvFrom = send_recv(clientSocket, heloCommand, '250')
        #Send MAIL FROM command and print server response.
        fromCommand='MAIL FROM: <%s@%s>' % (userName, userServer)
        recvFrom = send_recv(clientSocket, fromCommand, '250')
        #Send RCPT TO command and print server response.
        rcptCommand='RCPT TO: <%s@%s>' % (toName, toServer)
        recvRcpt = send_recv(clientSocket, rcptCommand, '250')
        #Send DATA command and print server response.
        dataCommand='DATA'
        dataRcpt = send_recv(clientSocket, dataCommand, '354')
        #Send message data.
        send(clientSocket, "Date: %s" % time.strftime("%a, %d %b %Y %H:%M:%S -0400", time.localtime()));
        send(clientSocket, "From: <%s@%s>" % (userName, userServer));
        send(clientSocket, "Subject: %s" % subjectValue);
        send(clientSocket, "To: %s@%s" % (toName, toServer));
        send(clientSocket, ""); #End of headers
        send(clientSocket, mailMessage);
        #Message ends with a single period.
        send_recv(clientSocket, ".", '250');
        #Send QUIT command and get server response.
        quitCommand='QUIT'
        quitRcpt = send_recv(clientSocket, quitCommand, '221')

        sendHttpResponse(connectionSocket)
        connectionSocket.close()
        clientSocket.close()
    except IndexError:
        print
    except KeyboardInterrupt:
        connectionSocket.close()
        clientSocket.close()
        print "Interrupted by CTRL-C\n"
        print "Exiting Mail Client\n"
        break

httpSocket.close()
