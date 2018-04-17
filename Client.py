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
## command implements
def upload(input, mySocket):
    mySocket.sendall(input)
    ip = mySocket.recv(1024)
    username = input.split(' ')[1].split('/')[0]
    filename = input.split(' ')[1].split('/')[1]
    try:
        server = loginName+'@'+ip
        directory = '/tmp/'+loginName+'/'+username+'/'
        r = os.system('ssh '+ server +' mkdir -p '+directory)
        command = 'scp -B '+ filename +' '+server+':'+directory
        result = os.system(command)
    except Exception as e:
        print(e)
    return result, ip

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
        result = result and (subInt >= 80 and subInt <= 100)
        return result

################################################################################
## main function
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
        inputList = input.rstrip().split(' ')
        if(len(inputList) != 2 or inputList[0] == None or inputList[0] == ''):
            wrongInput()
            continue
        if(inputList[0] == 'upload'):
            if(validateUp(inputList)):
                result, ip = upload(input,mySocket)
                if result == 0:
                    print(inputList[1].split('/')[1] \
                      +' has upload to '+ip)
                else:
                    print('upload fail')
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
        else:
            wrongInput()

        if(input == 'end'):
            break
    mySocket.close()
