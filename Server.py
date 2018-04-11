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
    print('1.','inputList', inputList)
    # validate Input()
    if(validate(inputList,serverIP) == True):
        return inputList[0], inputList[1:]
    else:
        return -1, []

def validate(inputList, serverIP):
    if len(inputList) != 5:
        print('2.',inputList, 'False')
        return False
    result = True
    for i, IP in enumerate(inputList):
        if i != 0:
            result = result and validateIP(serverIP, IP)
    print('3.',inputList, result)
    return result

def validateIP(serverIP, IP):
    subList = IP.split('.')
    subSList = serverIP.split('.')
    print('4.',subList, subSList)
    result = True
    if len(subList) != 4:
        print('5.',IP, 'False')
        return False
    else:
        result = result and  (subList[0] == '129' and subList[1] == '210' and subList[2] == '16')
        try:
            subInt = int(subList[3])
            subSInt = int(subSList[3])
        except:
            print('6.',IP, 'False')
            return False
        print(subInt, subSInt)
        result = result and (subInt >= 80 and subInt <= 100 and subInt != subSInt)
        print('7.',IP, result)
        return result

def getInput():
    inputs = ''
    line = sys.stdin.readline().rstrip('\n')
    while(line.rstrip() !=''):
        line = line.rstrip()
        inputs += line+' '
        print('line=',inputs)
        line = sys.stdin.readline().rstrip()
    return inputs.rstrip()

if __name__ == '__main__':
    HostName, serverIP = getServerInfo()

    partitionPower = -1
    #while(partitionPower == -1):
    partitionPower, HDIPList = getArgument(serverIP)
    if partitionPower == -1:
        print('invalid input')

    startServer()

