import pyAesCrypt
from cryptography.fernet import Fernet
import io
import json
from os import stat, path
import hashlib
import time

bufferSize = 1000 * 1024 # 1000KB
password = "bareissAdmin"
key = b'm-pPyZj6dfD1PjakTlYuqieUtlhSV_01ptqh96NMUcI='

def md5(fileName):
    # startTime = time.time()
    """Compute md5 hash of the specified file"""
    m = hashlib.md5()
    try:
        fd = open(fileName,"rb")
    except IOError:
        print ("Reading file has problem:{}".format(fileName))
        return
    x = fd.read()
    fd.close()
    m.update(x)
    # print(f'md5 takes {time.time()-startTime} seconds')
    return m.hexdigest()

def encryptFile(dictData, filepath):
    myjson = json.dumps(dictData)
    myBytejson = myjson.encode('utf8')
    # input plaintext binary stream
    fIn = io.BytesIO(myBytejson)
    with open(filepath, "wb") as fOut:
        pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)
    cksum = md5(filepath)
    return cksum

def decryptFile(filepath):
    cksum = md5(filepath)
    # get encrypted file size
    encFileSize = stat(filepath).st_size

    # decrypt
    with open(filepath, "rb") as fIn:
        # initialize decrypted binary stream
        fDec = io.BytesIO()
        # decrypt file stream
        pyAesCrypt.decryptStream(fIn, fDec, password, bufferSize, encFileSize)
        # to json
        decJsonByte = fDec.getvalue()
        myDict = json.loads(decJsonByte)
    return myDict, cksum

def encryptData(dictData):
    global key
    fernet = Fernet(key)
    myjson = json.dumps(dictData)
    myBytejson = myjson.encode('utf8')
    encrypted=fernet.encrypt(myBytejson)
    return encrypted

def encryptFile2(dictData, filepath):
    encrypted = encryptData(dictData)
    with open(filepath, "wb") as fOut:
        fOut.write(encrypted)
    cksum = md5(filepath)
    return cksum

def decryptData(myBytejson):
    global key
    fernet = Fernet(key)
    decrypted=fernet.decrypt(myBytejson)
    myDict = json.loads(decrypted)
    return myDict

def decryptFile2(filepath):
    cksum = md5(filepath)
    # decrypt
    with open(filepath, "rb") as fIn:
        myBytejson = fIn.read()
        myDict = decryptData(myBytejson)
    return myDict, cksum

if __name__=='__main__':
    # currFolder = path.dirname(__file__)
    # filePath = path.join(currFolder, 'eJson.ejson')
    # data = {'name': 'hello', 'value': 1, 'dataset': [{'nice':True}]}
    # startTime = time.time()
    # encryptFile(data, filePath)
    # print(f'encrypt file takes {time.time()-startTime} seconds')

    # startTime = time.time()
    # mydata, cksum = decryptFile('2ac571-06b-5dd-ffd-4611fe784b.eraw')
    # print(mydata)
    # print(f'decrypt file takes {time.time()-startTime} seconds')
    # print(mydata)
    # print(cksum)
    
    
    currFolder = path.dirname(__file__)
    filePath = path.join(currFolder, 'eJson.ejson')
    print(filePath)
    data = {'name': 'hello', 'value': 1, 'dataset': [{'nice':True}]}
    startTime = time.time()
    encryptFile2(data, filePath)
    print(f'encrypt file takes {time.time()-startTime} seconds')

    startTime = time.time()
    mydata, cksum = decryptFile2(filePath)
    print(mydata)
    print(f'decrypt file takes {time.time()-startTime} seconds')
    print(mydata)
    print(cksum)