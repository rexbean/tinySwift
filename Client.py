import sys
import socket
import os

def getClientInfo():
    loginName = os.popen('whoami').read()
    return loginName.rstrip('\n')

def getArgument():
    inputList = []
    # get Input
    input = getInput()
    # split input
    inputList = input.split(' ')
    # validate Input()
    if(validate(inputList) == True):
        return inputList[0], int(inputList[1])
    else:
        return 'invalid', -1

def getInput():
    inputs = ''
    line = sys.stdin.readline().rstrip('\n')
    while(line.rstrip() !=''):
        line = line.rstrip()
        inputs += line+' '
        line = sys.stdin.readline().rstrip()
    return inputs.rstrip()

def validate(inputList):
    if len(inputList) != 2:
        return False
    result = True
    result = result and validateIP(inputList[0])
    try:
        subInt = int(inputList[1])
    except:
        return false
    result = result and (subInt > 1023 and subInt < 65536)
    return result

def validateIP(IP):
    subList = IP.split('.')
    result = True
    if len(subList) != 4:
        return False
    else:
        result = result and  (subList[0] == '129' and subList[1] == '210' and subList[2] == '16')
        try:
            subInt = int(subList[3])
        except:
            return False
        result = result and (subInt >= 80 and subInt <= 100)
        return result

if __name__ == '__main__':
    loginName = getClientInfo()
    print('loginName='+loginName)
    IP = 'invalid'
    while(IP == 'invalid'):
        IP, port = getArgument()
    print('serverIp = '+IP+' port = ' + str(port))
    mySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mySocket.connect((IP,port))
    while 1:
        input = raw_input("Please input cmd:")
        #all lowercase
        inputList= input.split(' ')
        mySocket.sendall(input)
        data=mySocket.recv(1024)
        if(inputList[0] == 'upload'):
            username = inputList[1].split('')
            command = 'scp -B '+ loginName
        print data
        if(data == 'end'):
            break
    mySocket.close()
