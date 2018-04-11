import socket


def getArgument():
    inputList = []
    # get Input
    input = getInput()
    # split input
    inputList = input.split(' ')
    # validate Input()
    if(validate(inputList) == True):
        return inputList[0], inputList[1]
    else:
        return -1, -1

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

if __name__ == '__name__':
    IP, port = getArgument()
    mySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((IP,port))
    while 1:
        input=raw_input("Please input cmd:")
        print(input)
        s.sendall(cmd)
        data=s.recv(1024)
        print data
    s.close()
