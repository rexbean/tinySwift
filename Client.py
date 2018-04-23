import sys
import socket
import os



################################################################################
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

################################################################################
## command implements

## upload
def upload(input, mySocket):
    mySocket.send(input)
    ipList = mySocket.recv(1024)
    if ipList == '-1':
        print('upload fail! File has already existed!')
    else:
        username = input.split(' ')[1].split('/')[0]
        filename = input.split(' ')[1].split('/')[1]
        ip = ipList.split(' ')[0]
        ipBackup = ipList.split(' ')[1]
        up(ip,username, filename)
        up(ipBackup,username, filename)

def up(ip, username, filename):
    try:
        server = loginName+'@'+ip
        directory = '/tmp/'+loginName+'/'+username+'/'
        r = os.system('ssh '+ server +' mkdir -p '+directory)
        command = 'scp -B '+ filename +' '+server+':'+directory
        result = os.system(command)
        print(inputList[1].split('/')[1] \
          +' has upload to '+ip)
    except Exception as e:
        print(e)

################################################################################
## download
def download(input, mySocket):
    try:
        mySocket.send(input)
        ip = mySocket.recv(1024)

        username = input.split(' ')[1].split('/')[0]
        filename = input.split(' ')[1].split('/')[1]
        directory = '/tmp/'+loginName+'/'+username+'/'

        os.system('mkdir -p '+ username)
        ipList = ip.split(' ')
        print(ipList[0],ipList[1])
        if(ipList[0] == '-1' and ipList[1] == '-1'):
            print('Does not have this file!Please check!')
        elif(ipList[0] != '-1'):
            server = loginName+'@'+ipList[0]
            command = 'scp -B '+server+':'+directory+filename+ ' ./'+username
            os.system(command)
        elif(ipList[1] != '-1'):
            server = loginName+'@'+ipList[1]
            command = 'scp -B '+server+':'+directory+filename+ ' ./'+username
    except Exception as e:
        print(e)

###############################################################################3
## delete
def delete(input, mySocket):
    try:
        mySocket.send(input)
        comfirmation = mySocket.recv(1024)
        print(comfirmation)
        response = getInput()

        mySocket.send(response)
        result = mySocket.recv(1024)

        if(result == '1'):
            print('the file has been deleted successfully!')
        elif result == '0':
            print('the file has not been deleted!')
        elif result == '-1':
            print('delete fail!')
    except Exception as e:
        print(e)

################################################################################
## list
def myList(input, mySocket):
    try:
        mySocket.send(input)
        files = mySocket.recv(1024)
        if files != '-1':
            username = input.split(' ')[1]
            print(username+'has files:')
            fileList = files.split('$')
            length = len(fileList)
            for i in range(1,length):
                if(fileList[i]!=''):
                    print(fileList[i])
        else:
            print('Do not have this user!')
    except Exception as e:
        print(e)

################################################################################
## add
def add(input, mySocket):
    try:
        ip = input.split(' ')[1]
        if validateIP(ip) == False:
            print('The IP is invalid')
        else:
            mySocket.send(input)
            files = mySocket.recv(1024)
            fileList = files.split('$')
            for file in fileList:
                print(file)
    except Exception as e:
        print(e)

################################################################################
## remove
def remove(input, mySocket):
    try:
        ip = input.split(' ')[1]
        if validateIP(ip) == False:
            print('The IP is invalid')
        else:
            mySocket.send(input)
            files = mySocket.recv(1024)
            fileList = files.split('$')
            for file in fileList:
                print(file)
    except Exception as e:
        print(e)


################################################################################
## client information
def getClientInfo():
    loginName = os.popen('whoami').read()
    return loginName.rstrip('\n')


################################################################################
## process the input
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

def wrongInput():
    print("Invalid input")

################################################################################
## validate input
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
        result = result and (subInt >= 60 and subInt < 100)
        return result

################################################################################
## main function
if __name__ == '__main__':
    loginName = getClientInfo()
    print('loginName = '+loginName)
    IP = 'invalid'
    while(IP == 'invalid'):
        IP, port = getArgument()
    print('serverIp = '+IP+' port = ' + str(port))
    mySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mySocket.connect((IP,port))
    command=[]
    f = open('t14.dat')
    for line in f:
        command.append(line.rstrip())
    f.close()
    while 1:
        input = raw_input("Please input cmd:")
        #all lowercase
#    for input in command:
        if(input == 'end'):
            mySocket.send('end')
            break
        inputList = input.rstrip().split(' ')
        if(len(inputList) != 2 or inputList[0] == None or inputList[0] == ''):
            wrongInput()
            continue
        if(inputList[0] == 'upload'):
            if(validateUp(inputList)):
                upload(input,mySocket)
            else:
                wrongInput()
        elif (inputList[0] == 'list'):
            if(validateList(inputList)):
                myList(input, mySocket)
            else:
                wrongInput()
        elif (inputList[0] == 'download'):
            if(validateDown(inputList)):
                download(input, mySocket)
            else:
                wrongInput()
        elif (inputList[0] == 'delete'):
            if(validateDelete(inputList)):
                delete(input, mySocket)
            else:
                wrongInput()
        elif (inputList[0] == 'add'):
            if(validateAdd(inputList)):
                add(input, mySocket)
            else:
                wrongInput()
        elif (inputList[0] == 'remove'):
            if(validateRemove(inputList)):
                remove(input, mySocket)
            else:
                wrongInput()
        elif (inputList[0] == 'end'):
            closeServer(mySocket)
        else:
            wrongInput()
    mySocket.close()
