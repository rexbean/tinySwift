#!/usr/bin/python
import socket
import sys

def getServerInfo():
    # get server host name
    HostName = socket.getfqdn(socket.gethostname())
    # get server IP
    serverIP = socket.gethostbyname(HostName)

    return HostName, serverIP

def findAvailablePort(serverIP):
    port = 0
    while True:
        try:
            s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.bind((serverIP, 0))
            port = s.getsockname()[1]
            if(port > 1023):
                break
            s.close()
        except OSError as e:
            print(e)
    return s

def startServer(mySocket):
    mySocket.listen(1)
    print('Server is listening...')
    while 1:
        conn,addr=mySocket.accept()
        print'Connected by',addr
        try:
            while 1:
                data=conn.recv(1024)
                print(data)
                if data != 'end':
                    conn.sendall('hello!'+addr[0])
                else:
                    print('server is closing')
                    conn.sendall('end')
        except:
            break
        mySocket.close()


def getArgument(serverIP):
    inputList = []
    # get Input
    input = getInput()
    # split input
    inputList = input.split(' ')
    # validate Input()
    if(validate(inputList,serverIP) == True):
        return inputList[0], inputList[1:]
    else:
        return -1, []

def validate(inputList, serverIP):
    if len(inputList) != 5:
        return False
    result = True
    for i, IP in enumerate(inputList):
        if i != 0:
            result = result and validateIP(serverIP, IP)
    return result

def validateIP(serverIP, IP):
    subList = IP.split('.')
    subSList = serverIP.split('.')
    result = True
    if len(subList) != 4:
        return False
    else:
        result = result and  (subList[0] == '129' and subList[1] == '210' and subList[2] == '16')
        try:
            subInt = int(subList[3])
            subSInt = int(subSList[3])
        except:
            return False
        print(subInt, subSInt)
        result = result and (subInt >= 80 and subInt <= 100 and subInt != subSInt)
        return result

def getInput():
    inputs = ''
    line = sys.stdin.readline().rstrip('\n')
    while(line.rstrip() !=''):
        line = line.rstrip()
        inputs += line+' '
        line = sys.stdin.readline().rstrip()
    return inputs.rstrip()

if __name__ == '__main__':
    # get server hostName, serverIP
    HostName, serverIP = getServerInfo()

    # get and validate input
    partitionPower = -1
    #while(partitionPower == -1): # comment when using the test files
    partitionPower, HDIPList = getArgument(serverIP)
    if partitionPower == -1:
        print('invalid input')

    # get availablePort
    mySocket = findAvailablePort(serverIP)
    print ('hostname = '+HostName+' serverIp = '+serverIP \
    + 'port = '+str(mySocket.getsockname()[1]))

    # start server
    startServer(mySocket)
