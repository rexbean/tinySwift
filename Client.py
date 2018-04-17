import sys
import socket
import os



################################################################################
## command implements
def upload(input, mySocket):
    mySocket.sendall(input)
    ip = mySocket.recv(1024)
    username = input.spliet(' ')[1].split('/')[0]
    filename = input.spliet(' ')[1].split('/')[1]
    try:
        command = 'scp -B '+ filename +' '+loginName+'@'+ip+'/tmp/'\
            +loginName+'/'+username+'/'
            result = os.system(command)
    except Exception as e:
        print(e)
    print(result)
    return result

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
                disk = upload(input,mySocket)
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

        if(data == 'end'):
            break
    mySocket.close()
