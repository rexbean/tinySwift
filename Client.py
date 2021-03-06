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
        print(filename\
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
        print('The content of file are:')
        os.system('cat '+input.split(' ')[1])
        print('\n\n')
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
            print(username+' has files:')
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
        input = input if input[4:9] != 'linux' else 'add 129.210.16.'+str(100 - 60830 + int(input[9:14]))
        ip = input.split(' ')[1]
        if validateIP(ip) == False:
            print('The IP is invalid')
        else:
            mySocket.send(input)
            files = mySocket.recv(1024)
            fileList = files.split('@')
            originList = fileList[0].split('$')
            print('The following origin files have been moved:')
            for file in originList:
                print(file.split(' ')[0]+' has been moved to disk '+file.split(' ')[1])
            backupList = fileList[1].split('$')
            print('The following backup files have been moved:')
            for file in backupList:
                print(file.split(' ')[0]+' has been moved to disk '+file.split(' ')[1])
    except Exception as e:
        print(e)

################################################################################
## remove
def remove(input, mySocket):
    try:
        input = input if input[7:12] != 'linux' else 'remove 129.210.16.'+str(100 - 60830 + int(input[12:17]))
        ip = input.split(' ')[1]
        if validateIP(ip) == False:
            print('The IP is invalid')
        else:
            mySocket.send(input)
            files = mySocket.recv(1024)
            fileList = files.split('@')
            originList = fileList[0].split('$')
            print('The following origin files have been moved:')
            for file in originList:
                print(file.split(' ')[0]+' has been moved to disk '+ file.split(' ')[1])

            backupList = fileList[1].split('$')
            print('The following backup files have been moved:')
            for file in backupList:
                print(file.split(' ')[0]+' has been moved to disk '+ file.split(' ')[1])
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
    input = getInput().lower()
    # split input
    inputList = input.split(' ')
    # validate Input()
    IP = inputList[0]
    if IP[0:5]=='linux':
        #change to IP
        inputList[0]='129.210.16.'+str(100 - 60830 + int(IP[5:10]))
    elif IP[0:3]!='129':
        return 'invalid',-1
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
    IP = inputList[0]
    if(IP[0]=='1'):
        result = result and validateIP(inputList[0])
    else:
        return False
    try:
        subInt = int(inputList[1])
    except:
        return False
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
        result = result and (subInt >= 70 and subInt < 100)
        return result

def startClient(input):
    if(input == 'end'):
        mySocket.send('end')
        return
    inputList = input.rstrip().split(' ')
    if(len(inputList) != 2 or inputList[0] == None or inputList[0] == ''):
        wrongInput()
        return
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

################################################################################
## main function
if __name__ == '__main__':
    loginName = getClientInfo()
    print('Your loginName is '+loginName)
    IP = 'invalid'
    print('Please input 1 for autoTest using test file')
    print('Please input 2 for mannully test')
    choice = raw_input('please input your choice:')
    command=[]
    if choice.strip() == '1':
        f = open('t14.dat')
        for line in f:
           command.append(line.rstrip())
        f.close()
    while(IP == 'invalid'):
        print('Please Input IP address and port with space in between')
        print('If you input the hostName please just input the first part')
        print('e.g. linux60811.dc.engr.scu.edu, you should input linux60811')
        IP, port = getArgument()
        if IP == 'invalid':
            print('invalid input!please input again!')
    print('serverIp = '+IP+' port = ' + str(port))
    mySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mySocket.connect((IP,port))

    if choice == '1':
        for input in command:
            startClient(input)
        mySocket.close()
    elif choice == '2':
        while 1:
            input = raw_input("Please input cmd:")
            startClient(input)
        mySocket.close()
            #all lowercase
        #for input in command:
