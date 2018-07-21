# Client has been expanded and modified by Lester Hernandez Alfonso
# Main function structure and functions for STOR, RETR command are not
# entirely my original work. They are based on mutilple code pieces available
# at stack overflow. The rest of functions are my own work. Client is not in 
# working condition. However, it serves as a rough draft to implement the ftp
# client-server architecture required later in the course (starting this week).

#import necessary packages.
import os
import os.path
import errno
import traceback
import sys
from socket import *

#Global constants
USAGE = "usage: Python ftp hostname [username] [password]"


RECV_BUFFER = 1024
FTP_PORT = 21
CMD_USER = "USER"
CMD_PASS = "PASS"
CMD_QUIT = "QUIT"
CMD_HELP = "HELP"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LIST = "LIST"
CMD_PWD = "PWD"
CMD_PORT = "PORT"
CMD_DELE = "DELE"
CMD_STOR = "STOR"
CMD_RETR = "RETR"
CMD_CWD = "CWD"
CMD_CDUP = "CDUP"
CMD_STOA = "STOA"
CMD_APPE = "APPE"
CMD_RNFR = "RNFR"
CMD_RNTO = "RNTO"
CMD_RMD = "RMD"
CMD_MKD = "MKD"

#The data port starts at high number (to avoid privileges port 1-1024)
#the ports ranges from MIN to MAX
DATA_PORT_MAX = 61000
DATA_PORT_MIN = 60020
#data back log for listening.
DATA_PORT_BACKLOG = 1

#global variables
#store the next_data_port use in a formula to obtain
#a port between DATA_POR_MIN and DATA_PORT_MAX
next_data_port = 1


#global 
username = ""
password = "" 
hostname = "cnt4713.cs.fiu.edu"

#entry point main()
def main():
    global username
    global password
    global hostname 

    logged_on = False
    logon_ready = False
    print("FTP Client v1.0")
    if (len(sys.argv) < 2):
         print(USAGE)
    if (len(sys.argv) == 2):
        hostname = sys.argv[1]
    if (len(sys.argv) == 4):
        username = sys.argv[2]
        password = sys.argv[3]
        logon_ready = True


    print("********************************************************************")
    print("**                        ACTIVE MODE ONLY                        **")
    print("********************************************************************")
    print(("You will be connected to host:" + hostname))
    print("Type HELP for more information")
    print("Commands are NOT case sensitive\n")


    ftp_socket = ftp_connecthost(hostname)
    ftp_recv = ftp_socket.recv(RECV_BUFFER)
    #ftp_code = ftp_recv[:3]
    #
    #note that in the program there are many .strip('\n')
    #this is to avoid an extra line from the message
    #received from the ftp server.
    #an alternative is to use sys.stdout.write
    print(msg_str_decode(ftp_recv,True))
    #
    #this is the only time that login is called
    #without relogin
    #otherwise, relogin must be called, which included prompts
    #for username
    #
    if (logon_ready):
        logged_on = login(username,password,ftp_socket)

    keep_running = True

    while keep_running:
        try:
            rinput = input("FTP>")
            if (rinput is None or rinput.strip() == ''):
                continue
            tokens = rinput.split()
            cmdmsg , logged_on, ftp_socket = run_cmds(tokens,logged_on,ftp_socket)
            if (cmdmsg != ""):
                print(cmdmsg)
        except OSError as e:
        # A socket error
          print("Socket error:",e)
          strError = str(e)
          #this exits but it is better to recover
          if (strError.find("[Errno 32]") >= 0): 
              sys.exit()

    #print ftp_recv
    try:
        ftp_socket.close()
        print("Thank you for using FTP 1.0")
    except OSError as e:
        print("Socket error:",e)
    sys.exit()

def run_cmds(tokens,logged_on,ftp_socket):
    global username
    global password
    global hostname 

    cmd = tokens[0].upper()
   
    if (cmd == CMD_QUIT):
        quit_ftp(logged_on,ftp_socket)
        return "",logged_on, ftp_socket
    
    if (cmd == CMD_HELP):
        help_ftp()
        return "",logged_on, ftp_socket

    if (cmd == CMD_PWD):
        pwd_ftp(ftp_socket)
        return "",logged_on, ftp_socket

	if (cmd == CMD_CWD or cmd == CMD_RMD or cmd == CMD_MKD):
        directory_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket

	if (cmd == CMD_RNFR or cmd == CMD_RNTO):
        rename_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket

	if (cmd == CMD_CDUP):
        cdup_ftp(ftp_socket)
        return "",logged_on, ftp_socket

	if (cmd == CMD_NOOP):
        noop_ftp(ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_LIST):
        #FTP must create a channel to received data before
        #executing ls.
        #also makes sure that data_socket is valid
        #in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            list_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            return "[LS] Failed to get data port. Try again.",logged_on, ftp_socket

    if (cmd == CMD_LOGIN):
        username, password, logged_on, ftp_socket \
        = relogin(username, password, logged_on, tokens, hostname, ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_LOGOUT):
        logged_on,ftp_socket = logout(logged_on,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_DELE):
        delete_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_STOR or cmd == CMD_STOA or cmd == CMD_APPE):
        # FTP must create a channel to received data before
        # executing put.
        #  also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            put_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            return "[PUT] Failed to get data port. Try again.",logged_on, ftp_socket

    if (cmd == CMD_RETR):
        # FTP must create a channel to received data before
        # executing get.
        # also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            get_ftp(tokens, ftp_socket, data_socket)
            return "",logged_on, ftp_socket
        else:
            return "[GET] Failed to get data port. Try again.",logged_on, ftp_socket

    return "Unknown command", logged_on, ftp_socket

def str_msg_encode(strValue):
    msg = strValue.encode("ASCII")
    return msg

def msg_str_decode(msg,pStrip=False):
    #print("msg_str_decode:" + str(msg))
    strValue = msg.decode("ASCII")
    if (pStrip):
        strValue.strip('\n')
    return strValue

def ftp_connecthost(hostname):
    ftp_socket = socket(AF_INET, SOCK_STREAM)
    #to reuse socket faster. It has very little consequence for ftp client.
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, FTP_PORT))
    print (ftp_socket)
    return ftp_socket

def ftp_new_dataport(ftp_socket):
    global next_data_port
    dport = next_data_port
    host = gethostname()
    host_address = gethostbyname(host)
    next_data_port = next_data_port + 1 #for next next
    dport = (DATA_PORT_MIN + dport) % DATA_PORT_MAX

    print(("Preparing Data Port: " + host + " " + host_address + " " + str(dport)))
    data_socket = socket(AF_INET, SOCK_STREAM)
    # reuse port
    data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    data_socket.bind((host_address, dport))
    data_socket.listen(DATA_PORT_BACKLOG)

    #the port requires the following
    #PORT IP PORT
    #however, it must be transmitted like this.
    #PORT 192,168,1,2,17,24
    #where the first four octet are the ip and the last two form a port number.
    host_address_split = host_address.split('.')
    high_dport = str(dport // 256) #get high part
    low_dport = str(dport % 256) #similar to dport << 8 (left shift)
    port_argument_list = host_address_split + [high_dport,low_dport]
    port_arguments = ','.join(port_argument_list)
    cmd_port_send = CMD_PORT + ' ' + port_arguments + "\r\n"
    print(cmd_port_send)


    try:
        ftp_socket.send(str_msg_encode(cmd_port_send))
    except socket.timeout:
        print("Socket timeout. Port may have been used recently. wait and try again!")
        return None
    except socket.error:
        print("Socket error. Try again")
        return None
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return data_socket

def pwd_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("PWD\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


def get_ftp(tokens, ftp_socket, data_socket):
    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    remote_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = remote_filename

    ftp_socket.send(str_msg_encode("RETR " + remote_filename + "\r\n"))

    print(("Attempting to write file. Remote: " + remote_filename + " - Local:" + filename))

    msg = ftp_socket.recv(RECV_BUFFER)
    strValue = msg_str_decode(msg)
    tokens = strValue.split()
    if (tokens[0] != "150"):
        print("Unable to retrieve file. Check that file exists (LIST) or that you have permissions")
        return

    print(msg_str_decode(msg,True))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename, "wb")  # write and binary modes

    size_recv = 0
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        encoded_data = data_connection.recv(RECV_BUFFER)
		if (TRANSFER_TYPE == "A"):
			data = msg_str_decode(encoded_data,True)

        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            file_bin.write(data)
            size_recv += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


### put_ftp
def put_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) < 2):
        print(tokens[0] + " [filename]. Please specify filename")
        return

    local_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = local_filename

    if (os.path.isfile(local_filename) == False):
        print(("Filename does not exisit on this client. Filename: " + filename + " -- Check file name and path"))
        return
    filestat = os.stat(local_filename)
    filesize = filestat.st_size

	ftp_socket.send(str_msg_encode(tokens[0] + " " + filename + "\r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

    print(("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize)))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename,"rb") #read and binary modes

    size_sent = 0
    #use write so it doesn't produce a new line (like print)
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
		data = file_bin.read(RECV_BUFFER)
        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
			if (TRANSFER_TYPE == "A"):
				data = str_msg_encode(data)
			data_connection.send(data)
            size_sent += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


#
def list_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) > 1):
        ftp_socket.send(str_msg_encode("LIST " + tokens[1] + "\r\n"))
    else:
        ftp_socket.send(str_msg_encode("LIST\r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

    data_connection, data_host = data_socket.accept()

    msg = data_connection.recv(RECV_BUFFER)
    while (len(msg) > 0):
        print(msg_str_decode(msg,True))
        msg = data_connection.recv(RECV_BUFFER)

    data_connection.close()
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    #data_connection.close()

def delete_ftp(tokens, ftp_socket):

    if (len(tokens) < 2):
        print("You must specify a file to delete")
    else:
        print(("Attempting to delete " + tokens[1]))
        ftp_socket.send(str_msg_encode("DELE " + tokens[1] + "\r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

def logout(lin, ftp_socket):
    if (ftp_socket is None):
        print("Your connection was already terminated.")
        return False, ftp_socket

    if (lin == False):
        print("You are not logged in. Logout command will be send anyways")

    print("Attempting to logged out")
    msg = ""
    try:
        ftp_socket.send(str_msg_encode("QUIT\r\n"))
        msg = ftp_socket.recv(RECV_BUFFER)
    except socket.error:
        print ("Problems logging out. Try logout again. Do not login if you haven't logged out!")
        return False
    print(msg_str_decode(msg,True))
    ftp_socket = None
    return False, ftp_socket #it should only be true if logged in and not able to logout

def quit_ftp(lin,ftp_socket):
    print ("Quitting...")
    logged_on, ftp_socket = logout(lin,ftp_socket)
    print("Thank you for using FTP")
    try:
        if (ftp_socket is not None):
            ftp_socket.close()
    except socket.error:
        print ("Socket was not able to be close. It may have been closed already")
    sys.exit()


def relogin(username,password,logged_on,tokens,hostname,ftp_socket):
    if (len(tokens) < 3):
        print("LOGIN requires more arguments. LOGIN [username] [password]")
        print("You will be prompted for username and password now")
        username = input("User:")
        password = input("Pass:")
    else:
        username = tokens[1]
        password = tokens[2]

    if (ftp_socket is None):
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER)
        
        print(msg_str_decode(ftp_recv,True))

    logged_on = login(username, password, ftp_socket)
    return username, password, logged_on, ftp_socket


def help_ftp():
    print("FTP Help")
    print("Commands are not case sensitive")
    print("")
    print((CMD_QUIT + "\t\t Exits ftp and attempts to logout"))
    print((CMD_LOGIN + "\t\t Logins. It expects username and password. LOGIN [username] [password]"))
    print((CMD_LOGOUT + "\t\t Logout from ftp but not client"))
    print((CMD_LS + "\t\t prints out remote directory content"))
    print((CMD_PWD + "\t\t prints current (remote) working directory"))
    print((CMD_GET + "\t\t gets remote file. GET remote_file [name_in_local_system]"))
    print((CMD_PUT + "\t\t sends local file. PUT local_file [name_in_remote_system]"))
    print((CMD_DELETE + "\t\t deletes remote file. DELETE [remote_file]"))
    print((CMD_HELP + "\t\t prints help FTP Client"))


def login(user, passw, ftp_socket):
    if (user == None or user.strip() == ""):
        print("Username is blank. Try again")
        return False;


    print(("Attempting to login user " + user))
    #send command user
    ftp_socket.send(str_msg_encode(CMD_USER + " " + user + "\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    ftp_socket.send(str_msg_encode(CMD_PASS + " " + passw + "\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    strValue = msg_str_decode(msg,False)
    tokens = strValue.split()
    print(msg_str_decode(msg,True))
    if (len(tokens) > 0 and tokens[0] != "230"):
        print("Not able to login. Please check your username or password. Try again!")
        return False
    else:
        return True


def directory_ftp(tokens, ftp_socket):
	if (len(tokens) < 2):
        print(tokens[0] + " [directory]. Please specify directory path")
	else:
		directory = tokens[1]
		if(CMD_CWD == tokens[0]):
			print("Attempting to change remote working directory to: " + directory)
		if(CMD_RMD == tokens[0]):
			print("Attempting to remove remote directory: " + directory)
		if(CMD_MKD == tokens[0]):
			print("Attempting to create remote directory: " + directory)

		ftp_socket.send(str_msg_encode(tokens[0] + " " + directory + "\r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


def cdup_ftp(ftp_socket):
	print("Attempting to change remote working directory to parent directory of current directory")
    ftp_socket.send(str_msg_encode(CMD_CDUP + "\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


def rename_ftp(tokens, ftp_socket):
	if (len(tokens) < 2):
        print("tokens[0] [pathname]. Please specify file pathname")
	else:
		pathname = tokens[1]
		ftp_socket.send(str_msg_encode(tokens[0] + " " + pathname + "\r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


def noop_ftp(ftp_socket):
	ftp_socket.send(str_msg_encode("NOOP\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


#Calls main function.
main()
