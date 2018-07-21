#!/usr/bin/python
#HTTPserver.py
#Last version tested at http://ocelot.aul.fiu.edu:45679/hello.html
#An HTTP server that accepts and fulfills GET requests.
#Current version adds:
#Fixed the problem that was preventing the correct file extension
#from displaying. The path for os.path.isfile for some reason had 
#to be absolute.
#Server works as it should. Language files are displayed correctly.

import sys
from socket import socket, SOCK_STREAM, AF_INET, timeout
from datetime import datetime
import pytz
import os

def findLastModified(filename):
    seconds = os.path.getmtime(filename)
    last_modified_object = datetime.fromtimestamp(seconds, pytz.utc)
    return last_modified_object

def condGetHandler(connectionSocket, filename, date):

    dateobject = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z ")
    gmt = pytz.timezone("GMT")
    dateobject = gmt.localize(dateobject)

    last_modified_object = findLastModified(filename)

    if dateobject > last_modified_object:
        sendError(connectionSocket, '304', 'Not Modified')
    else:
        last_modified_date = datetime.strftime(last_modified_object, "%a, %d %b %Y %H:%M:%S GMT")
        sendFile(connectionSocket, filename, last_modified_date)

def sendFile(connectionSocket, filename, date):
    #In case "file.ext" does not exist but "file.ext.en" does
    cwd = os.getcwd()
    filePath = cwd + "/" + filename

    if not os.path.isfile(filePath):
        filename = filename + ".en"
    
    if date == '':
        last_modified_object = findLastModified(filename)
        date = date + datetime.strftime(last_modified_object, "%a, %d %b %Y %H:%M:%S GMT")    

    headerline1 = "HTTP/1.1 200 OK\r\n"
    headerline2 = "Last-Modified: " + date + "\r\n"
    headerline3 = "Content-Length: "
    headerline4 = "Content-Type: text/html\r\n"
    headerline5 = "Cache-Control: no-cache, no-store\r\n\r\n"
    response = ''

    message = ''
    file = open(filename,"r")
    while True:
        sys.stdout.write("*")
        data = file.read(4096)
        if (not data or data == '' or len(data) <= 0):
            file.close()
            break
        else:
            message = message + data

    print("\n")
    
    headerline3 = headerline3 + str(len(message)) + "\r\n"
 
    response = response + headerline1 + headerline2 + headerline3 + headerline4 + headerline5 + message
    connectionSocket.send(response)
    print "Response:\n" + response
     
def sendError(connectionSocket, errorNumber, description):
     headerline1 = "HTTP/1.1 " + errorNumber + " " + description + "\r\n"
     headerline2 = "Content-Length: 0\r\n"
     headerline3 = "Content-Type: text/plain\r\n\r\n"
     response = ''
    
     if (errorNumber == '304'):
         response = response + headerline1 + "\r\n"

     elif errorNumber == '404':
         headerline3 = "Content-Type: text/html; charset=iso-8859-1\r\n\r\n"
         notFoundMessage = ("<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\">\n"
                            " <html>\n"
                            " <head>\n"
                            "    <title>404 Not Found</title>\n"
                            " </head>\n"
                            " <body>\n"
                            "    <h1>Not Found</h1>\n"
                            " <p>The requested URL was not found on this server.</p>\n"
                            " </body>\n"
                            " </html>\n")
         headerline2 = "Content-Length: " + str(len(notFoundMessage)) + "\r\n"
         response = headerline1 + headerline2 + headerline3 + notFoundMessage

     else:
         response = response + headerline1 + headerline2 + headerline3
     
     connectionSocket.send(response)
     print "Response:\n" + response
    

def findLanguageFilename(filename, languages):
    for lang in languages:
        print lang
        langFile = filename +  "." + lang
        cwd = os.getcwd()
        langFilePath = cwd + "/" + langFile
        if os.path.isfile(langFilePath):
            print langFile
            return langFile

    print filename
    return filename
    


#Create a TCP socket 
#Notice the use of SOCK_STREAM for TCP packets
serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort=45679
# Assign IP address and port number to socket
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print "Interrupt with CTRL-C"
 
while True:
        try:
                #Establish the connection
                print 'Ready to serve...'
                connectionSocket, addr = serverSocket.accept()
                connectionSocket.settimeout(10)
                print "Connection from %s port %s" % addr
                message = ''
                #Receive the client packets
                while 1:
                    data = connectionSocket.recv(4096)
                    print "Received: " + str(len(data)) + " bytes"
                    message = message + data
                    if len(data) < 4096:
                        break 

                print "Request: "
                print message
                tokens = message.split()
                filename = tokens[1].partition("/")[2]
 
                #Process Accept-Language header
                #Will get value error if not found. Execution continues.
                acceptLang = tokens.index("Accept-Language:")
                index = acceptLang + 1
                languages = tokens[index].split(',')

                index = 0
                for lang in languages:
                    languages[index] = lang.split(';')[0]
                    index = index + 1

                langFilename = findLanguageFilename(filename, languages)
                
                #If language is negotiated don't do conditional get
                if (filename == langFilename):
                    #Will get ValueError if header not found. Execution continues.
                    condGet = tokens.index("If-Modified-Since:")
                    index = condGet + 1
                    date = ''
            
                    while index < (condGet + 7):
                        date = date + tokens[index] + " "
                        index = index + 1
               
                    condGetHandler(connectionSocket, filename, date)
                else:
                    sendFile(connectionSocket, langFilename, '')

                connectionSocket.close()

        except ValueError:
                try:
                    sendFile(connectionSocket, filename, '')
                    connectionSocket.close()
                except(IOError,OSError):
                    print "404 - Not found %s\n" %filename
                    sendError(connectionSocket, '404', 'Not Found')
                    connectionSocket.close()
        except timeout:
                print "408 Request Timeout - Connection Closed\n"
                sendError(connectionSocket, '408', 'Request Timeout')
                connectionSocket.close()
        except (IOError,OSError):
                print "404 - Not found %s\n" %filename
                sendError(connectionSocket, '404', 'Not Found')
                connectionSocket.close()
        except IndexError:
                print "408 Request Timeout - Connection Closed\n"
                sendError(connectionSocket, '408', 'Request Timeout')
                connectionSocket.close()
        except KeyboardInterrupt:
                print "\nInterrupted by CTRL-C\n"
                connectionSocket.close()
                break

serverSocket.close()

