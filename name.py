import math
import hashlib




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

def getInput():
    inputs = []
    line = sys.stdin.readline().rstrip('\n')
    while(line.rstrip() !=''):
        line = line.rstrip()
        inputs.append(line)
        line = sys.stdin.readline().rstrip()
    return inputs

if __name__ == '__main__':
    inputs = getInput()
    for input in inputs:
        consistentHashing(input)
