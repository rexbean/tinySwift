#!/usr/bin/python
import socket
import sys
import os
import hashlib
import math
import datetime
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
################################################################################
## upload
def upload(inputList, conn):
    disk = 0
    try:
        disk = consistentHashing(inputList[1])
        if myGlobal.originDict.has_key(inputList[1]):
            print('A file with same has already existed!')
            result = '-1'
        else:
            updateTableUp(inputList, disk)
            result = myGlobal.diskList[disk]
            print(inputList[1].split('/')[1] \
                  +' will upload to disk'+ str(disk)+' : '+myGlobal.diskList[disk])
    except Exception as e:
        print(e)
        result = '-1'
    finally:
        conn.send(result)



################################################################################
## download
def download(inputList, conn):
    
    originDisk = searchOriginTable(inputList)
    backupDisk = searchBackupTable(inputList)
    print(originDisk, backupDisk)
    if originDisk == -1 and backupDisk == -1:
        print('Cannot find this file!')
        result = '-1 -1'
    elif originDisk == -1:
        print('original Disk does not have this file')
        print('backup file is on disk '+ str(backupDisk))
        result = '-1'
        result +=' '+myGlobal.diskList[backupDisk]
    elif backupDisk == -1:
        print('original file is on disk' + str(originDisk))
        print('backup Disk does not have this file')
        result = myGloal.diskList[originDisk]
        result += ' -1'
    else:
        print('original file is on disk' + str(originDisk))
        print('backup file is on disk' + str(backupDisk))
        result = myGlobal.diskList[originDisk]+' '+myGlobal.diskList[backupDisk]
    print(result)
    conn.send(result)

################################################################################
## delete
def delete(inputList, conn):
    conn.send('Do you really want to delete this file?')
    input = conn.recv(1024)
    ## lowercase
    if input == 'yes' or input == 'y':
        originDisk = searchOriginTable(inputList)
        backupDisk = searchBackupTable(inputList)
        print(originDisk,backupDisk)
        try:
            updateTableDelete(originDisk, backupDisk, inputList)
            if originDisk == -1 and backupDisk == -1:
                print('Cannot find this file!')
                result = '-1'
            else:
                print('the file has been deleted successfully!')
                result = '1'
        except Excetion as e:
            print(e)
            result = '-1'
        finally:
            conn.send(result)
    else:
        print('The file has not been deleted!')
        conn.send('0')

################################################################################
## list

def myList(inputList, conn):
    result = ''
    username = inputList[1]
    fileList = []
    try:
        if myGlobal.userDict.has_key(username):
            fileList = myGlobal.userDict[username]
            print('Files are :')
            for file in fileList:
                result += file + '$'
                print(file)
            result = result.rstrip()
        else:
            myGlobal.userDict[username] = fileList
            print('Cannot find User!')
            result = '-1'
    except Exception as e:
        print(e)
        result = '-a'
    finally:
        conn.send(result)

################################################################################
## add

# def add(inputList,conn):



################################################################################
## manipulate table

def updateTableUp(inputList, disk):
    updateStoreTableUp(inputList, disk)
    updateUserTableUp(inputList, disk)
    updateNumberTableUp(disk)
    updateNumberTableUp(disk+1)

def updateTableDelete(originDisk, backupDisk, inputList):
    result = updateStoreTableDelete(originDisk,backupDisk,inputList)
    result = result and updateUserTableDelete(inputList)
    updateNumberTableDelete(originDisk, backupDisk)
    return result

def updateStoreTableUp(inputList, disk):
    myGlobal.originDict[inputList[1]] = disk
    myGlobal.backupDict[inputList[1]] = disk + 1
    print('update store table success!')

def updateUserTableUp(inputList,disk):
    fileList = []
    username = inputList[1].split('/')[0]
    filename = inputList[1].split('/')[1]

    nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if myGlobal.userDict.has_key(username):
        fileList = myGlobal.userDict[username]
        fileList.append(filename+' disk '+str(disk)+' '+nowTime)
    else:
        fileList.append(filename+' disk '+str(disk)+' '+nowTime)
        myGlobal.userDict[username] = fileList
    print('update user table success!')

def updateNumberTableUp(disk):
    number = 0
    if myGlobal.numberDict.has_key(disk):
        number = myGlobal.numberDict[disk]
        myGlobal.numberDict[disk] = number+1
    else:
        myGlobal.numberDict[disk] = number+1

def updateNumberTableDelete(originDisk, backupDisk):
    number = 0

    if originDisk == -1 and backupDisk == -1:
        print('update number table fail!')
        return False
    elif originDisk == -1:
        if myGlobal.numberDict.has_key(backupDisk):
            number = myGlobal.numberDict[backupDisk]
            myGlobal.numberDict[backupDisk] = number-1
    elif backupDisk == -1:
        if myGlobal.numberDict.has_key(originDisk):
            number = myGlobal.numberDict[originDisk]
            myGlobal.numberDict[originDisk] = number-1
    else:
        if myGlobal.numberDict.has_key(backupDisk):
            number = myGlobal.numberDict[backupDisk]
            myGlobal.numberDict[backupDisk] = number-1
        if myGlobal.numberDict.has_key(originDisk):
            number = myGlobal.numberDict[originDisk]
            myGlobal.numberDict[originDisk] = number-1


def updateStoreTableDelete(originDisk, backupDisk,inputList):
    if originDisk == -1 and backupDisk == -1:
        print('update store table fail!')
        return False
    elif originDisk == -1:
        myGlobal.backupDict[inputList[1]] == -1
    elif backupDisk == -1:
        myGlobal.originDict[inputList[1]] == -1
    else:
        myGlobal.backupDict[inputList[1]] == -1
        myGlobal.originDict[inputList[1]] == -1
    print('update store table success!')
    return True

def updateUserTableDelete(inputList):
    username = inputList[1].split('/')[0]
    filename = inputList[1].split('/')[1]
    fileList = []
    if myGlobal.userDict.has_key(username):
        fileList = myGlobal.userDict[username]
        for file in fileList:
            if file.split(' ')[0] == filename:
                fileList.remove(file)
        print('update user table success!')
        return True
    else:
        myGlobal.userDict[username] = fileList
        print('Cannot find User!')

def searchOriginTable(inputList):
    try:
        if inputList[1] in myGlobal.originDict:
            print('in')
            disk = myGlobal.originDict[inputList[1]]
            print(disk)
            return disk
        else:
            return -1
    except Exception as e:
        print(e)

def searchBackupTable(inputList):
    try:
        if inputList[1] in myGlobal.backupDict:
            print('in')
            disk = myGlobal.backupDict[inputList[1]]
            print(disk)
            return disk
        else:
            return -1
    except Exception as e:
        print(e)

################################################################################
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
        print('Connected by',addr)
        try:
            while 1:
                print('$'),
                inputList = []
                input = conn.recv(1024)
                if(input is None):
                    wrongInput(conn)
                    return False
                ## do all lowercase
                print('input='+input)
                if input == '':
                    break
                inputList = input.rstrip().split(' ')
                if(len(inputList) != 2 or inputList[0] == None):
                    wrongInput(conn)
                elif (inputList[0] == 'upload'):
                    if(validateUp(inputList)):
                        upload(inputList,conn)
                elif (inputList[0] == 'list'):
                    if(validateList(inputList)):
                        myList(inputList, conn)
                elif (inputList[0] == 'download'):
                    if(validateDown(inputList)):
                        download(inputList, conn)
                elif (inputList[0] == 'delete'):
                    if(validateDelete(inputList)):
                        delete(inputList, conn)
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
