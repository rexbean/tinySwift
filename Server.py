#!/usr/bin/python
import socket
import sys

def getServerInfo():
    # get server host name
    HostName = socket.getfqdn(socket.gethostname(  ))
    # get server IP
    serverIP = socket.gethostbyname(HostName)

    print('HostName =', HostName, 'serverIP=', serverIP)
    return HostName, serverIP

def findAvailablePort(serverIP):
    cPort = 0
    port = 1024
    ports = []

    while port < 1300:
        try:
            s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.bind((serverIP, port))
            print(str(port)+" is available")
            s.close()
        except OSError as e:
            print(e)
        finally:
            port += 1



def startServer():
    # get the IP address of the server
    # get the available port of the machine
    # print the IP address, host name, port of the Server
    print ("IP = , Server=")

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
    HostName, serverIP = getServerInfo()

    # partitionPower = -1
    # #while(partitionPower == -1): # comment when using the test files
    # partitionPower, HDIPList = getArgument(serverIP)
    # if partitionPower == -1:
    #     print('invalid input')

    ports = findAvailablePort(serverIP)

    startServer()
