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
            result = myGlobal.diskList[disk]+' '+myGlobal.diskList[getNextDisk(disk,len(myGlobal.diskList))]
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
            myGlobal.numOriginDict[n - 1] = 0
            myGlobal.numBackupDict[n - 1] = 0
            result = moveOriginAdd(n)
            result = result[:-1]
            result += '@'
            result += moveBackupAdd(n)
            result = result[:-1]
            print('add '+result)
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
        if(validateIP(myGlobal.serverIP,ip)):
            if ip in myGlobal.diskList:
                result = moveRemove(ip)
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

def moveRemove(ip):
    try:
        result = ''
        numToMoveOrigin = {}
        numToMoveBackup = {}
        disk = findDisk(ip)
        n = len(myGlobal.diskList) - 1
        print(disk, n)
        numOrigin = myGlobal.numOriginDict[disk]
        numBackup = myGlobal.numBackupDict[disk]
        print('numOrigin = ',str(numOrigin),'numBackup = ',str(numBackup))
        for i in range(0, n):
            numToMoveOrigin[i] = numOrigin / n
            numToMoveBackup[i] = numBackup / n
            print('numToMoveOrigin = ',numToMoveOrigin)
            print('numToMoveBackup = ',numToMoveBackup)

        result = move(disk, myGlobal.originDict, myGlobal.backupDict, numToMoveOrigin)
        print('remove result = ',result)
        result = result[:-1]
        result += '@'
        result += move(disk, myGlobal.backupDict, myGlobal.originDict, numToMoveBackup)
        result = result[:-1]
        print('remove result = ',result)
    except Exception as e:
        print('remove move',e)
    return result


def findDisk(ip):
    for i, disk in enumerate(myGlobal.diskList):
        if disk == ip:
            print(ip +' is the ip addr of the disk '+str(i))
            return i
    return -1

def move(disk, table, tableBackup, numToMove):
    try:
        result = ''
        index = 0
        n = len(numToMove)
        for path in table:
            if table[path] == disk:
                if(tableBackup[path] != index):
                    if(numToMove[index] == 0):
                        tmp = getNextDisk(index, n)
                        if(tableBackup[path] == tmp or tmp == n - 1):
                            tmp = getNextDisk(index,n)
                        index = getNextDisk(index, n)
                        if index == n - 1:
                            index = 0
                    else:
                        tmp = index
                else:
                    tmp = getNextDisk(index, n)
                    if tmp == n-1:
                        tmp = 0
                        print('get next disk= '+str(tmp))
                deleteStoreTable(table, path)
                moveCommand(path, myGlobal.diskList[disk], myGlobal.diskList[tmp])
                result += path+' '+str(tmp)+'$'
                if table == myGlobal.originDict:
                    myGlobal.numOriginDict[disk] = myGlobal.numOriginDict[disk] - 1
                    myGlobal.numOriginDict[tmp] = myGlobal.numOriginDict[tmp] + 1
                    userTableRemove(path)
                    userTableAdd(path, tmp)
                elif table == myGlobal.backupDict:
                    myGlobal.numBackupDict[disk] = myGlobal.numBackupDict[disk] - 1
                    myGlobal.numBackupDict[tmp] = myGlobal.numBackupDict[tmp] + 1
                updateStoreTable(table, path, tmp)
                numToMove[tmp] -= 1
    except Exception as e:
        print('move ',e)
    return result

def getNextDisk(originDisk, n):
    if originDisk + 1 == n:
        return 0
    else:
        return originDisk + 1


def moveOriginAdd(n):
    originNumToMove = computeNumToMove(myGlobal.numOriginDict, n)
    result =  moveOriginToNewDisk(originNumToMove, n)
    print(result)
    return result


def moveBackupAdd(n):
    backupNumToMove = computeNumToMove(myGlobal.numBackupDict, n)
    result = moveBackupToNewDisk(backupNumToMove, n)
    print('movebackupadd '+result)
    return result
def moveOriginToNewDisk(numToMove, n):
    result = ''
    table = myGlobal.originDict
    count = 0
    for i in numToMove:
        if i > 0:
            count += 1

    for path in table:
        disk = table[path]
        if(numToMove[disk] > 0):
            deleteStoreTable(table, path)
            moveCommand(path, myGlobal.diskList[disk], myGlobal.diskList[n - 1])
            myGlobal.numOriginDict[disk] = myGlobal.numOriginDict[disk] -1
            myGlobal.numOriginDict[n - 1] = myGlobal.numOriginDict[n - 1] + 1
            updateStoreTable(table, path, n - 1)
            result+= path +' ' + str((n-1))+'$'
            userTableRemove(path)
            userTableAdd(path, n - 1)
            numToMove[disk] -= 1
            if numToMove[disk] == 0:
                count= count - 1
                if(count == 0):
                    break
    return result

def moveBackupToNewDisk(numToMove,n):
    result = ''
    table = myGlobal.backupDict
    count = 0
    for i in numToMove:
        if i > 0:
            count += 1
    for path in table:
        disk = table[path]
        if(numToMove[disk] > 0):
            # prevent the original and backup in the same disk
            if(myGlobal.originDict[path] == n - 1 ):
                continue
            deleteStoreTable(table, path)
            moveCommand(path, myGlobal.diskList[disk], myGlobal.diskList[n - 1])
            myGlobal.numBackupDict[disk] = myGlobal.numBackupDict[disk]-1
            myGlobal.numBackupDict[n - 1] = myGlobal.numBackupDict[n - 1] + 1
            updateStoreTable(table, path, n - 1)
            result +=path +' '+str((n-1))+'$'
            numToMove[disk] -= 1
            if numToMove[disk] == 0:
                count= count - 1
                if(count == 0):
                    break
    return result

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
    updateStoreTableUp(inputList, disk, getNextDisk(disk,len(myGlobal.diskList)))
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
    updateNumberTable(myGlobal.numBackupDict, getNextDisk(disk,len(myGlobal.diskList)), 1)

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
        fileList.append(filename+' disk '+str(disk)+':'+myGlobal.diskList[disk]+' '+nowTime)
    else:
        fileList.append(filename+' disk '+str(disk)+':'+myGlobal.diskList[disk]+' '+nowTime)
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
            return disk
        else:
            return -1
    except Exception as e:
        print(e)

def searchBackupTable(inputList):
    try:
        if inputList[1] in myGlobal.backupDict:
            disk = myGlobal.backupDict[inputList[1]]
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

def check():
    print('checking whether files are exist...')
    try:
        for path in myGlobal.originDict:
            disk = myGlobal.originDict[path]
            diskIP = myGlobal.diskList[disk]
            result = os.system('ssh '+ diskIP +' stat /tmp/'+myGlobal.loginName+'/'+path+' >/dev/null 2>&1')
            print('origin '+path +' exists on origin disk')
            if result != 0:
                print(path+' on origin disk has been deleted')
                restore(path, 0)


        for path in myGlobal.backupDict:
            disk = myGlobal.backupDict[path]
            diskIP = myGlobal.diskList[disk]
            result = os.system('ssh '+ diskIP +' stat /tmp/'+myGlobal.loginName+'/'+path+' >/dev/null 2>&1')
            print('backup '+path +' exists on backup disk')
            if result != 0:
                print(path +' on backup disk has been deleted')
                restore(path, 1)
    except Exception as e:
        print(e)

def restore(path, origin):
    if origin == 0:
        disk = myGlobal.backupDict[path]
        diskOrigin = myGlobal.originDict[path]
        diskIP = myGlobal.diskList[disk]
        diskIPOrigin = myGlobal.diskList[diskOrigin]
        result = os.system('ssh '+ diskIP + ' stat /tmp/'+myGlobal.loginName+'/'+path+' >/dev/null 2>&1')
        if result == 0:
            moveCommand(path, diskIP, diskIPOrigin)
            print(path+' has been restored from backup disk')
        else:
            print(path+' do not in backup disk either')
    else:
        disk = myGlobal.originDict[path]
        diskBackup = myGlobal.backupDict[path]
        diskIP = myGlobal.diskList[disk]
        diskIPBackup = myGlobal.diskList[diskBackup]
        result = os.system('ssh '+ diskIP + ' stat /tmp/'+myGlobal.loginName+'/'+path+' >/dev/null 2>&1')
        if result == 0:
            moveCommand(path, diskIP, diskIPBackup)
            print(path+' has been restored from origin disk')
        else:
            print(path+' do not in origin disk either')

def startServer(mySocket):
    mySocket.listen(1)
    print('Server is listening...')
    try:
        while 1:
            conn,addr=mySocket.accept()
            print('Connected by',addr)
            while 1:
                print('$'),
                inputList = []
                input = conn.recv(1024)
                if(input is None):
                    wrongInput(conn)
                    return False
                ## do all lowercase
                print('input='+input)
                if input == 'end':
                    conn.close()
                    break
                inputList = input.rstrip().split(' ')
                check()
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
                else:
                    wrongInput(conn)
    except:
        conn.close()
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
            if IP[0] == '1':
                result = result and validateIP(serverIP, IP)
            elif IP[0] == 'l':
                result = result and validateHost(serverIP, IP)
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
        result = result and (subInt >= 70 and subInt < 100 and subInt != subSInt)
        return result

def validateHost(serverIP, IP):
    subSList = serverIP.split('.')
    subSInt = int(subSList[3])
    result = True
    if len(IP) != 10:
        print('a')
        return False
    if IP[0:5] != 'linux':
        print('b')
        return False
    num = int(IP[5:10])

    if num > 60830 or num < 60800:
        print('c')
        return False
    if num == (subSInt+60730):
        print('d')
        return False
    return True

def getInput():
    inputs = ''
    line = sys.stdin.readline().rstrip('\n')
    while(line.rstrip() !=''):
        line = line.rstrip()
        inputs += line+' '
        line = sys.stdin.readline().rstrip()
    return inputs.rstrip()

def changeToIP(HostList):
    newList = []
    for host in HostList:
        if host[0] == 'l':
            host = '129.210.16.'+str(100 - 60830 + int(host[5:10]))
            newList.append(host)
        else:
            newList.append(host)
    return newList
def InitialTable():
    for i in range(0,4):
        myGlobal.numOriginDict[i] = 0
        myGlobal.numBackupDict[i] = 0

################################################################################
## main function
if __name__ == '__main__':
    # get server hostName, serverIP
    HostName, serverIP = getServerInfo()

    # get and validate input
    partitionPower = -1
    while(partitionPower == -1): # comment when using the test files
        print('please input partitionPower and four disk IP Address')
        print('If you want to use hostname, please only input the first part of the host name, like linu6011')
        partitionPower, HDIPList = getArgument(serverIP)
        if partitionPower == -1:
            print('invalid input')
    ## change all Host Name to IP
    newList = changeToIP(HDIPList)

    myGlobal.partitionPower = partitionPower
    myGlobal.diskList = newList
    myGlobal.serverIP = serverIP
    myGlobal.hostname = HostName
    InitialTable()

    # get availablePort
    mySocket = findAvailablePort(serverIP)
    print ('hostname = '+HostName+'\nserverIp = '+serverIP\
    + '\nport = '+str(mySocket.getsockname()[1]))

    # start server
    startServer(mySocket)
