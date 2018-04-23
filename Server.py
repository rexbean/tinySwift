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
            result = myGlobal.diskList[disk]+' '+myGlobal.diskList[getNextDisk[disk]]
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
    try:
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
    except Exception as e:
        print(e)
        result = e
    finally:
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
        #print(originDisk,backupDisk)
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
    result = '$'
    username = inputList[1]
    fileList = []
    try:
        if username in myGlobal.userDict:
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
def add(inputList,conn):
    try:
        ip = inputList[1]
        if(validateIP(myGlobal.serverIP,ip)):
            # add new disk to the list
            myGlobal.diskList.append(ip)
            n = len(myGlobal.diskList)
            result = moveOriginAdd(n)
            moveBackupAdd(n)
            print(result)
            result = result[:-1]
        else:
            result = 'invalid ip, please resend'
            print(result)
    except Exception as e:
        print('add',e)
        result = e
    finally:
        conn.send(result)

################################################################################
## remove
def remove(inputList, conn):
    try:
        result = ''
        ip = inputList[1]
        if(validate(myGlobal.serverIP,ip)):
            if ip in myGlobal.diskList:
                result = moveRemove()
            else:
                result = 'ip does no in the disk list, please resend'
                print(result)
        else:
            result = 'invalid ip, please resend'
            print(result)
    except Exception as e:
        print(e)
        result = e
    finally:
        conn.send(result)




################################################################################

def moveRemove():
    disk = myGlobal.findDisk(ip)
    n = len(myGlobal.diskList) - 1
    numOrigin = myGlobal.numOriginDict[disk]
    numBackup = myGlobal.numBackupDict[disk]

    for i in range(0, n):
        numToMoveOrigin[i] = numOrigin / n
        numToMoveBackup[i] = numBackup / n

    result = move(disk, myGlobal.originDict, myGlobal.backupDict, numToMoveOrigin)
    result += move(disk, myGlobal.backupDict, myGlobal.originDict, numToMoveBackup)

    return result


def findDisk(ip):
    for i, disk in enumerate(myGlobal.diskList):
        if disk == ip:
            print(ip +'is the ip addr of the disk'+disk)
            return i
    return -1

def move(disk, table, tableBackup, numToMove):
    result = ''
    index = 0
    for path in table:
        if table[path] == disk:
            if(tableBackup[path] != index):
                if(numToMove[index] == 0):
                    tmp = index + 1
                    index += 1
                else:
                    tmp = index
            else:
                tmp = getNextDisk(index, n)
            deleteStoreTable(table, path)
            moveCommand(path, myGloba.diskList[disk], myGlobal.diskList[tmp])
            result += path+' '+str(disk)+'$'
            if table == myGlobal.originDict:
                userTableRemove(path)
                userTableAdd(path, tmp)
            updateStoreTable(table, path, tmp)
            numToMoveOrigin[tmp] -= 1
    return result

def getNextDisk(originDisk, n):
    if originDisk + 1 == n:
        return 0
    else:
        return originDisk + 1


def moveOriginAdd(n):
    originNumToMove = computeNumToMove(myGlobal.numOriginDict, n)
    print('originNumToMove',originNumToMove)
    result =  moveOriginToNewDisk(originNumToMove, n)
    print(result)
    return result


def moveBackupAdd(n):
    backupNumToMove = computeNumToMove(myGlobal.numBackupDict, n)
    print('backupNumToMove',backupNumToMove)
    moveBackupToNewDisk(backupNumToMove, n)

def moveOriginToNewDisk(numToMove, n):
    print('moveOriginToNewDisk')
    result = ''
    table = myGlobal.originDict
    count = 0
    for i in numToMove:
        if i > 0:
            count += 1

    for path in table:
        disk = table[path]
        if(numToMove[disk] > 0):
            print(str(disk),numToMove[disk])
            deleteStoreTable(table, path)
            moveCommand(path, myGlobal.diskList[disk], myGlobal.diskList[n - 1])
            updateStoreTable(table, path, n - 1)
            result+= path +' ' + str((n-1))+'$'
            userTableRemove(path)
            userTableAdd(path, n - 1)
            numToMove[disk] -= 1
        elif numToMove[disk] == 0:
            print('count='+count)
            count= count - 1
        if(count == 0):
            break
    print('moveOriginToNewDisk',result)
    return result

def moveBackupToNewDisk(numToMove,n):
    print('moveBackupToNewDisk')
    table = myGlobal.backupDict
    count = 0
    for i in numToMove:
        if i > 0:
            count += 1
    for path in table:
        disk = table[path]
        if(numToMove[disk] > 0):
            print(str(disk),numToMove[disk])
            # prevent the original and backup in the same disk
            if(myGlobal.originDict[path] == n - 1 ):
                continue
            deleteStoreTable(table, path)
            moveCommand(path, myGloba.diskList[disk], myGloba.diskList[n - 1])
            updateStoreTable(table, path, n - 1)
            numToMove[disk] -= 1
        elif numToMove[disk] == 0:
            print('count='+count)
            count= count - 1

        if(count == 0):
            break
    print('moveBackupToNewDisk over')

def computeNumToMove(table, n):
    print(table)
    numToMove = []
    for i, num in enumerate(table):
        if i in table:
            numToMove.append(table[i]/n)
    print('has computed num to move')
    return numToMove


def moveCommand(path, source, destination):
    username = path.split('/')[0]
    filename = path.split('/')[1]
    root = '/tmp/'+myGlobal.loginName+'/'
    directory = '/tmp/'+myGlobal.loginName+'/'+username+'/'
    cMkdir = 'ssh '+ destination + ' mkdir -p '+ directory
    r = os.system(cMkdir)
    command = 'scp -B '+source+':'+root+path+' '+destination+':'+directory
    result = os.system(command)


################################################################################
## manipulate table

def updateTableUp(inputList, disk):
    updateStoreTableUp(inputList, disk, getNextDisk(disk))
    updateUserTableUp(inputList, disk)
    updateNumberTableUp(disk)


def updateTableDelete(originDisk, backupDisk, inputList):
    result = updateStoreTableDelete(inputList, originDisk,backupDisk)
    result = result and updateUserTableDelete(inputList)
    updateNumberTableDelete(originDisk, backupDisk)
    return result





## update store table
def updateStoreTableUp(inputList, originDisk, backupDisk):
    updateStoreTable(myGlobal.originDict, inputList[1], originDisk)
    updateStoreTable(myGlobal.backupDict, inputList[1], backupDisk)
    print('update store table success!')


def updateStoreTableDelete(inputList, originDisk, backupDisk):
    try:
        if originDisk == -1 and backupDisk == -1:
            print('update store table fail!')
            return False
        else:
            deleteStoreTable(myGlobal.originDict, inputList[1])
            deleteStoreTable(myGlobal.backupDict, inputList[1])
            print('update store table success!')
            return True
    except Exception as e:
        print('updateStoreTableDelete',e)


def deleteStoreTable(table, path):
    try:
        del table[path]
        print(path+' has been removed')
    except Exception as e:
        print('deleteStoreTable',e)

def updateStoreTable(table, path, disk):
    table[path] = disk
    print(path+' has been saved on disk'+ str(disk))



## update number table
def updateNumberTableUp(disk):
    updateNumberTable(myGlobal.numOriginDict, disk, 1)
    updateNumberTable(myGlobal.numBackupDict, getNextDisk(disk), 1)

def updateNumberTableDelete(originDisk, backupDisk):
    if originDisk == -1 and backupDisk == -1:
        print('update number table fail!')
        return False
    elif originDisk == -1:
        updateNumberTable(myGlobal.numBackupDict, backupDisk, -1)
    elif backupDisk == -1:
        updateNumberTable(myGlobal.numOriginDict, originDisk, -1)
    else:
        updateNumberTable(myGlobal.numBackupDict, backupDisk, -1)
        updateNumberTable(myGlobal.numOriginDict, originDisk, -1)

def updateNumberTable(table, disk , value):
    number = 0
    if disk in table:
        number = table[disk]
        table[disk] = number + value
    else:
        table[disk] = number + value


##user table
def userTableRemove(path):
    fileList = []
    print(path)
    username = path.split('/')[0]
    filename = path.split('/')[1]
    if username in myGlobal.userDict:
        fileList = myGlobal.userDict[username]
        for file in fileList:
            if file.split(' ')[0] == filename:
                fileList.remove(file)
        print('update user table success!')
        return True
    else:
        myGlobal.userDict[username] = fileList
        print('Cannot find User!')

def userTableAdd(path, disk):
    fileList = []
    username = path.split('/')[0]
    filename = path.split('/')[1]
    nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if username in myGlobal.userDict:
        fileList = myGlobal.userDict[username]
        fileList.append(filename+' disk '+str(disk)+' '+nowTime)
    else:
        fileList.append(filename+' disk '+str(disk)+' '+nowTime)
        myGlobal .userDict[username] = fileList
    print('update user table success!')

def updateUserTableDelete(inputList):
    userTableRemove(inputList[1])


def updateUserTableUp(inputList,disk):
    userTableAdd(inputList[1], disk)




def searchOriginTable(inputList):
    try:
        if inputList[1] in myGlobal.originDict:
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
    code = getMD5SUM(name)
    i_code = int(code, 16) >> 112
    try:
        piece = math.pow(2,(float)(myGlobal.partitionPower))/4
    except Exception as e:
        print(e)
    if(i_code >= 0 and i_code < piece):
        return 0
    elif(i_code >= piece and i_code < 2 * piece ):
        return 1
    elif(i_code >= 2 * piece and i_code < 3 * piece):
        return 2
    elif(i_code >= 3 * piece and i_code < 4 * piece):
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

    myGlobal.loginName = os.popen('whoami').read().rstrip('\n')

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
                    else:
                        wrongInput(conn)
                elif (inputList[0] == 'list'):
                    if(validateList(inputList)):
                        myList(inputList, conn)
                    else:
                        wrongInput(conn)
                elif (inputList[0] == 'download'):
                    if(validateDown(inputList)):
                        download(inputList, conn)
                    else:
                        wrongInput(conn)
                elif (inputList[0] == 'delete'):
                    if(validateDelete(inputList)):
                        delete(inputList, conn)
                    else:
                        wrongInput(conn)
                elif (inputList[0] == 'add'):
                    if(validateAdd(inputList)):
                        print(add(inputList, conn))
                    else:
                        wrongInput(conn)
                elif (inputList[0] == 'remove'):
                    if(validateRemove(inputList)):
                        print(remove(inputList, conn))
                    else:
                        wrongInput(conn)
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
        result = result and (subInt >= 60 and subInt < 100 and subInt != subSInt)
        return result

def getInput():
    inputs = ''
    line = sys.stdin.readline().rstrip('\n')
    while(line.rstrip() !=''):
        line = line.rstrip()
        inputs += line+' '
        line = sys.stdin.readline().rstrip()
    return inputs.rstrip()

def InitialTable():
    for i in range(0,4)
        myGlobal.numOriginDict[i] = 0
        myGlobal.numBackupDict[i] = 0

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
    myGlobal.serverIP = serverIP
    myGlobal.hostname = HostName
    InitialTable()

    # get availablePort
    mySocket = findAvailablePort(serverIP)
    print ('hostname = '+HostName+'\nserverIp = '+serverIP\
    + '\nport = '+str(mySocket.getsockname()[1]))

    # start server
    startServer(mySocket)
