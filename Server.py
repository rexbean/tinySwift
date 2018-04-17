#!/usr/bin/python
import socket
import sys
import os
import hashlib
import math
import myGlobal


################################################################################
## command functions
def wrongInput(conn):
    print('wrong input!')
    conn.send('wrong input! Please input again')

def closeServer(conn):
    print('server is closing')
    conn.send('end')


## validate command input
def validateUp(inputList):
    return validateFile(inputList)

def validateDown(inputList):
    return validateFile(inputList)

def validateDelete(inputList):
    return validateFile(inputList)

def validateList(inputList):
    return validateTwoArgs(inputList)

def validateAdd(inputList):
    return validateTwoArgs(inputList)

def validateRemove(inputList):
    return validateTwoArgs(inputList)


def validateTwoArgs(inputList):
    if(len(inputList) != 2):
        return False
    else:
        return True

def validateFile(inputList):
    argumentList = inputList[1].split('/')
    if(len(argumentList) != 2):
        return False
    else:
        return True

## command implements

def upload(inputList, conn):
    disk = 0
    try:
        disk = consistentHashing(inputList[1])
        conn.send(myGlobal.diskList[disk])
    except Exception as e:
        print(e)
    return disk 

def download(inputList, conn):
    if(findFile(inputList[1])):
        result = ''
        conn.send(result)
    else:
        result = 'Cannot find the file'
    return result

def delete(inputList, conn):
    if(findFile(inputList[1])):
        result = ''
        conn.send(result)
    else:
        result = 'Cannot find the file'
    return result

def myList(inputList, conn):
    if(findUser(inputList[1])):
        result = getFiles(inputList[1])
        conn.send(result)
    else:
        result = 'Cannot find user'
    return result

##def add(inputList, conn):
def consistentHashing(name):
    print(name)
    code = getMD5SUM(name)
    print('0x'+code)
    i_code = int(code, 16) >> 112
    print(hex(i_code))
    print(myGlobal.partitionPower)
    try:
        piece = math.pow(2,(float)(myGlobal.partitionPower))
    except Exception as e:
        print(e)
    print('piece:',piece)
    if(i_code >= 0 and i_code < piece):
        print('disk Zero')
        return 0
    elif(i_code >= piece and i_code < 2 * piece ):
        print('disk One')
        return 1
    elif(i_code >= 2 * piece and i_code < 3 * piece):
        print('disk Two')
        return 2
    elif(i_code >= 3 * piece and i_code < 4 * piece):
        print('disk Four')
        return 3

def findFile(name):
    return consistentHashing(name)

def getMD5SUM(name):
    myMd5 = hashlib.md5()
    myMd5.update(name)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest




################################################################################
##functions for Server
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
        print('Connected by'+ addr)
        try:
            while 1:
                print('$'),
                inputList = []
                input = conn.recv(1024)
                if(input is None):
                    wrongInput(conn)
                    return False
                ## do all lowercase
                print(input)
                inputList = input.rstrip().split(' ')
                if(len(inputList) != 2 or inputList[0] == None or inputList[0] == ''):
                    wrongInput(conn)
                elif (inputList[0] == 'upload'):
                    if(validateUp(inputList)):
                        disk = upload(inputList,conn)
                        print(inputList[1].split('/')[1] \
                              +' will upload to disk'+ str(disk)+' : '+myGlobal.diskList[disk])
                elif (inputList[0] == 'list'):
                    if(validateList(inputList)):
                        print(myList(inputList, conn))
                elif (inputList[0] == 'download'):
                    if(validateDown(inputList)):
                        print(download(inputList, conn))
                elif (inputList[0] == 'delete'):
                    if(validateDelete(inputList)):
                        print(delete(inputList, conn))
                elif (inputList[0] == 'add'):
                    if(validateAdd(inputList)):
                        print(add(inputList, conn))
                elif (inputList[0] == 'remove'):
                    if(validateRemove(inputList)):
                        print(remove(inputList, conn))
                elif (inputList[0] == 'end'):
                    closeServer(conn)
                    return True
                else:
                    wrongInput(conn)
                    return False
        except:
            break
        mySocket.close()

################################################################################
## do something with the input
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
        result = result and (subInt >= 80 and subInt < 100 and subInt != subSInt)
        return result

def getInput():
    inputs = ''
    line = sys.stdin.readline().rstrip('\n')
    while(line.rstrip() !=''):
        line = line.rstrip()
        inputs += line+' '
        line = sys.stdin.readline().rstrip()
    return inputs.rstrip()

################################################################################
## main function
if __name__ == '__main__':
    # get server hostName, serverIP
    HostName, serverIP = getServerInfo()

    # get and validate input
    partitionPower = -1
    #while(partitionPower == -1): # comment when using the test files
    partitionPower, HDIPList = getArgument(serverIP)
    if partitionPower == -1:
        print('invalid input')

    myGlobal.partitionPower = partitionPower
    myGlobal.diskList = HDIPList

    # get availablePort
    mySocket = findAvailablePort(serverIP)
    print ('hostname = '+HostName+'\nserverIp = '+serverIP\
    + '\nport = '+str(mySocket.getsockname()[1]))

    # start server
    startServer(mySocket)
