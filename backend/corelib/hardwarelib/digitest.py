import sys, os
import time
import re

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
DB_DIR = SCRIPT_DIR
indentLevel = 2
for i in range(indentLevel):
    DB_DIR = os.path.split(DB_DIR)[0]
sys.path.append(os.path.normpath(os.path.join(PACKAGE_PARENT,SCRIPT_DIR)))
sys.path.append(os.path.normpath(DB_DIR))
print(sys.path)
from baInstr import BaInstr
import random

class RotationState:
    def __init__(self):
        self.N = 0
        self.n = 0
        self.index = 0
        self.pathList = []
        self.atHome = False
        self.foundHome = False
    
    def setPathList(self, N, n):
        self.N = N
        self.n = n
        self.pathList = [(sample_N+1, location_n+1) for sample_N in range(self.N) for location_n in range(self.n)]
        print('pathlist: {}'.format(self.pathList))
    
    def getCurrentPos(self):
        if self.foundHome:
            if len(self.pathList) == 0:
                return (0,0)
            else:
                if self.atHome:
                    return (0,0)
                else:
                    return self.pathList[self.index]
        else:
            return (0,0)

    def getNextPos(self):
        curIndex = self.index
        if self.foundHome:
            if len(self.pathList) == 0:
                return (0,0)
            else:
                if self.atHome:
                    curIndex = 0
                else:
                    curIndex += 1
                # nxtIndex = self.index % len(self.pathList)
                print('length of self.pathList: {}'.format(len(self.pathList)))
                print('self.index: {}'.format(curIndex))
                # print('nxtIndex: {}'.format(nxtIndex))
                print('')
                self.atHome = False
                return self.pathList[curIndex]
        else:
            return (0,0)
        
    def getLastPos(self):
        curIndex = self.index
        if self.foundHome:
            if len(self.pathList) == 0:
                return (0,0)
            else:
                if self.atHome:
                    curIndex = -1
                else:
                    curIndex -= 1
                self.atHome = False
                return self.pathList[curIndex]
        else:
            return (0,0)

    def setHomePos(self, findHomeOk):
        self.foundHome = findHomeOk
        if self.foundHome:
            self.atHome = True
            self.index = 0
        else:
            self.atHome = False
    
    def setPosition(self, N, n):
        print('N {}, n {}'.format(N,n))
        newIdx = N*n - 1
        self.index = newIdx % len(self.pathList)
        self.atHome = False

class Digitest(BaInstr):
    def __init__(self):
        super(Digitest, self).__init__()
        self.rotStatus = RotationState()

    def setRotation(self):
        N,n = self.get_rotation_info()
        if N:
            self.rotStatus.setPathList(N, n)

    def set_remote(self, enabled=True):
        if enabled:
            ret = self.write_and_read('SET','DEV_REMOTE_CONTROL','TRUE')
        else:
            ret = self.write_and_read('SET','DEV_REMOTE_CONTROL','FALSE')
        return ret

    def get_remote(self):
        return self.write_and_read('GET', 'MS_MODE')
    
    def start_mear(self):
        self.write_and_read('MS_PRO', 'START')
        return True
    
    def start_mear_direct(self):
        self.write_and_read('MS_PRO', 'SINGLE')
        return True
    
    def stop_mear(self):
        self.write_and_read('MS_PRO', 'STOP')
    
    def set_mode(self, mode):
        self.write_and_read('SET', 'MS_MODE', mode)
        return True
    
    def set_std_mode(self):
        self.set_mode('STANDARD_M')
        return True
    
    def set_std_graph_mode(self):
        self.set_mode('STANDARD_GRAPH_M')
        return True
    
    def set_std_pk_mode(self):
        self.set_mode('STANDARD_PK_M')
    
    def set_hysterese_mode(self):
        self.set_mode('HYSTERESE_M')
    
    def get_mode(self):
        return self.write_and_read('GET', 'MS_MODE')
    
    def get_single_value(self, dummyTemp=0):
        ret = self.write_and_read('GET','MS_VALUE')
        if ret == 'FINISHED':
            try:
                data = self.readline_only()
                return 1, float(data)
            except:
                return -1, None
        elif ret == 'DISTANCE_TOO_BIG':
            return -1, None
        else:
            return 0, None
    
    def get_buffered_value(self, buffer=13):
        while True:
            data = self.device.readline().decode('utf-8').strip()
            if self.debug:
                print("Graph data resp: {}".format(data))
            resp_reg = ''' ?([\d.]*)> ?([\d.]*)'''
            match = re.search(resp_reg, data)
            ret = None
            if match:
                ret = {}
                ret['time'] = float(match.groups()[0])
                ret['value'] = float(match.groups()[1])
                yield True, ret['time'], ret['value'], "ok"
            else:
                ret = self.parse_resp(data.encode('utf-8'))
                if ret:
                    if ret['value'] == 'FINISHED':
                        break
                    else:
                        yield False, 0, 0, ret['value']
                        break
    
    def get_suitable_mode(self):
        ret = self.get_ms_method().lower()
        resp_reg = '''(shore)?(asker)?(type)?'''
        match = re.search(resp_reg, ret)
        if match:
            return ['STANDARD_M','STANDARD_GRAPH_M', 'STANDARD_PK_M']
        
        resp_reg = '''(irhd))?(vlrh)?'''
        match = re.search(resp_reg, ret)
        if match:
            return ['STANDARD_M','STANDARD_GRAPH_M', 'HYSTERESE_M']

    def isConnectRotation(self):
        try:
            ret = self.write_and_read('GET','DEV_OPTION')
            if ret == '"ROTATION DC"':
                return True
            else:
                return False
        except:
            return False

    def get_rotation_info(self):
        if self.isConnectRotation():
            sampleSize = int(self.write_and_read('GET','DEV_OPT_ROT_N'))
            mearCounts = int(self.write_and_read('GET','DEV_OPT_ROT_n'))
            return sampleSize, mearCounts
        else:
            return None,None
    
    def set_rotation_home(self):
        if self.isConnectRotation():
            ret = self.write_and_read('ROT_Nn','{},{}'.format(0,0))
            if ret == '"OUT OF RANGE"':
                # self.rotStatus.setHomePos(False)
                return False, ret
            else:
                while True:
                    sampleSize, mearCounts = self.get_rotation_info()
                    if sampleSize:
                        break
                    time.sleep(0.25)
                return True, 'ok'
        else:
            return True, 'ok'
    
    def set_rotation_pos(self,sample_N, mear_pos_n):
        if self.isConnectRotation():
            ret = self.write_and_read('ROT_Nn','{},{}'.format(sample_N,mear_pos_n))
            if ret == '"OUT OF RANGE"':
                return False, ret
            else:
                while True:
                    sampleSize, mearCounts = self.get_rotation_info()
                    if sampleSize:
                        break
                    time.sleep(0.25)
                return True, 'ok'
        else:
            return True, 'ok'
    
    def goNext(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getNextPos()
            print('')
            print('############ Next Position N{} n{}'.format(N,n))
            print('')
            success, res = self.set_rotation_pos(N,n)
            return success, res
        else:
            return True, 'ok'

    def goLast(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getLastPos()
            success, res = self.set_rotation_pos(N,n)
            return success, res
        else:
            return True, 'ok'

    def goNextSample(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getCurrentPos()
            nextN = N + 1
            sampleSize, mearCounts = self.get_rotation_info()
            if N == sampleSize:
                nextN = 1
            success, res = self.set_rotation_pos(nextN,n)
            return success, res
        else:
            return True, 'ok'

    def goLastSample(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getCurrentPos()
            nextN = N - 1
            sampleSize, mearCounts = self.get_rotation_info()
            if N == 1 or N <=0 :
                nextN = sampleSize
            success, res = self.set_rotation_pos(nextN,n)
            return success, res
        else:
            return True, 'ok' 

class GelomatDigitest(Digitest):
    def __init__(self):
        super().__init__()
    
    def get_lift(self):
        return self.write_and_read('GET', 'MS_LIFT')    
    def set_lift(self,lift):
        self.write_and_read('SET', 'MS_LIFT', lift)
    def get_method(self):
        return self.write_and_read('GET', 'MS_METHOD')
    def set_mode(self,mode='"STD_M"'):
        self.write_and_read('SET', 'MS_MODE', mode)
    def get_single_value(self):
        while True:
            time.sleep(0.1)
            data = self.readline_only()
            if data:
                time.sleep(5)
                return 1, float(data)

class DummyDigitest(BaInstr):
    def __init__(self):
        super(DummyDigitest, self).__init__()
        self.dummyCounter = 0
        self.dummyType = '"ROTATION DC"'
        self.sampleCounts = 25
        self.mearCounts = 3
        self.rotStatus = RotationState()
    
    def readline_only(self):
        resp = 'dummyResp'
        if self.debug:
            print("original resp in readline only: {}".format(resp))
        resp = 'dummyResp'
        if self.debug:
            print("parsing resp in readline only: {}".format(resp))
        if resp:
            return 'dummyResp'
        else:
            return None
    
    def write_and_read(self,cmd, para, value=None):
        max_wait_count = 200
        counter = 0
        return True
    
    def open(self, port=None, baudrate=9600, bytesize=None, parity=None, stopbits=None, timeout=None):
        self.device = None
        self.connected = True
        return self.device
    
    def close(self):
        self.connected = False

    def setRotation(self):
        N,n = self.get_rotation_info()
        if N:
            self.rotStatus.setPathList(N, n)

    def get_dev_name(self):
        return 'DummyDigitest'
    
    def get_dev_software_version(self):
        return 'DummyVersion1.0'

    def get_ms_duration(self):
        self.duration = 3.0
        return self.duration

    def set_ms_duration(self, value):
        self.duration = float(value)
        return self.duration

    def get_ms_method(self):
        return 'ShoreA'

    def isReady(self):
        ret = 'Ready'
        if ret:
            if ret[2] == 'ACTIVE':
                return False
            else:
                return True
        else:
            return False
    
    def set_remote(self, enabled=True):
        if enabled:
            print('SET','DEV_REMOTE_CONTROL','TRUE')
        else:
            print('SET','DEV_REMOTE_CONTROL','FALSE')

    def get_remote(self):
        return 'ShoreA'
    
    def start_mear(self):
        print('MS_PRO', 'START')
    
    def start_mear_direct(self):
        print('MS_PRO', 'SINGLE')
    
    def stop_mear(self):
        print('MS_PRO', 'STOP')
    
    def set_mode(self, mode):
        print('SET', 'MS_MODE', mode)
    
    def set_std_mode(self):
        self.set_mode('STANDARD_M')
    
    def set_std_graph_mode(self):
        self.set_mode('STANDARD_GRAPH_M')
    
    def set_std_pk_mode(self):
        self.set_mode('STANDARD_PK_M')
    
    def set_hysterese_mode(self):
        self.set_mode('HYSTERESE_M')
    
    def get_mode(self):
        return 'STANDARD_M'
    
    def get_single_value(self, dummyTemp=0):
        time.sleep(0.1)
        if self.dummyCounter*0.1 < self.duration:
            ret = '"DEVICE BUSY"'
            self.dummyCounter += 1
        else:
            ret = 'FINISHED'
            self.dummyCounter = 0

        if ret == '"DEVICE BUSY"':
            return 0, None
        elif ret == 'FINISHED':
            time.sleep(0.1)
            noise = random.random()*3
            ret = 0.0016 * dummyTemp * dummyTemp - 0.2468 * dummyTemp + 57.073 + noise
            return 1, ret
        else:
            return -1, None
    
    def get_buffered_value(self, buffer=13):
        while True:
            time.sleep(0.1)
            if self.dummyCounter < buffer:
                match = True
                ret = None
                self.dummyCounter += 1
            else:
                match = False
                ret = True
                self.dummyCounter = 0

            if match:
                ret = {}
                ret['time'] = self.dummyCounter * 0.1
                ret['value'] = random.random()*100
                yield True, ret['time'], ret['value'], "ok"
            else:
                if ret:
                    ret = {}
                    ret['value'] = 'FINISHED'
                    if ret['value'] == 'FINISHED':
                        break
                    else:
                        yield False, 0, 0, 'DEVICE BUSY'
                        break
    
    def get_suitable_mode(self):
        ret = 'ShoreA'.lower()
        resp_reg = '''(shore)?(asker)?(type)?'''
        match = re.search(resp_reg, ret)
        if match:
            return ['STANDARD_M','STANDARD_GRAPH_M', 'STANDARD_PK_M']
        
        resp_reg = '''(irhd))?(vlrh)?'''
        match = re.search(resp_reg, ret)
        if match:
            return ['STANDARD_M','STANDARD_GRAPH_M', 'HYSTERESE_M']

    def isConnectRotation(self):
        ret = self.dummyType
        if ret == '"ROTATION DC"':
            return True
        else:
            return False

    def get_rotation_info(self):
        if self.isConnectRotation():
            sampleSize = self.sampleCounts
            mearCounts = self.mearCounts
            return sampleSize, mearCounts
        else:
            return None,None
    
    def set_rotation_home(self):
        if self.isConnectRotation():
            ret = True
            if ret == '"OUT OF RANGE"':
                # self.rotStatus.setHomePos(False)
                return False, ret
            else:
                # self.rotStatus.setHomePos(True)
                return True, 'ok'
        else:
            return True, 'ok'
    
    def set_rotation_pos(self,sample_N, mear_pos_n):
        print('')
        print('############ Next Position N {}, n {} ##########'.format(sample_N,mear_pos_n))
        print('')
        # self.rotStatus.setPosition(sample_N, mear_pos_n)
        return True, 'ok'
    
    def goNext(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getNextPos()
            success, res = self.set_rotation_pos(N,n)
            return success, res
        else:
            return True, 'ok'

    def goLast(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getLastPos()
            success, res = self.set_rotation_pos(N,n)
            return success, res
        else:
            return True, 'ok'      

    def goNextSample(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getCurrentPos()
            nextN = N + 1
            sampleSize, mearCounts = self.get_rotation_info()
            if N == sampleSize:
                nextN = 1
            success, res = self.set_rotation_pos(nextN,n)
            return success, res
        else:
            return True, 'ok'

    def goLastSample(self):
        if self.isConnectRotation():
            (N, n) = self.rotStatus.getCurrentPos()
            nextN = N - 1
            sampleSize, mearCounts = self.get_rotation_info()
            if N == 1 or N <=0 :
                nextN = sampleSize
            success, res = self.set_rotation_pos(nextN,n)
            return success, res
        else:
            return True, 'ok' 
def main():
    ba = DummyDigitest()
    # input = b'GET(MS_MODE),' # exp_crc = '05F9' 
    # result = ba.get_cksum(input)
    # print(result)

    def print_data(data):
        print('I am callback: {}'.format(data))


    # resp = 'E0000,MS_DURATION=5,30AA\r\n'
    # par_result = ba.parse_resp(resp)
    # print(par_result)
    ba.open("COM3")
    ret = ba.get_dev_name()
    print(ret)
    ret = ba.get_dev_software_version()
    print(ret)
    ret = ba.get_ms_method()
    print(ret)
    ba.config(debug=True)
    ba.set_remote(True)
    ba.set_mode('STANDARD_M')
    duration_s = 1
    ret = ba.set_ms_duration(duration_s)
    print(ret)
    for i in range(3):
        time.sleep(0.1)
        ba.set_remote(True)
        ba.start_mear()
        
        while True:
            statusCode, value = ba.get_single_value()
            print('final resp of step {}: {}'.format(i, value))
            if statusCode == 1:
                break
            elif statusCode < 0:
                print('distance too big when measuring')
                break
            else:
                time.sleep(0.1)
    
    # ret = ba.set_remote(False)

    # ret = ba.set_remote(True)
    
    # ret = ba.set_mode('STANDARD_GRAPH_M')
    # print(ret)
    # duration_s = 10
    # ret = ba.set_ms_duration(duration_s)
    # print(ret)
    # ba.config(debug=True)
    # ret = ba.start_mear()
    # print('I am waiting for result')
    
    # getBuffer = ba.get_buffered_value()
    # for b in getBuffer:
    #     print(b)
    
    
    ba.config(wait_cmd=True)
    ba.set_remote(False)

    ba.close()

    # plt.plot(x,y)
    # plt.show()

def test_rotation():
    ba = Digitest()
   
    ba.open("COM5")
    print(ba.isConnectRotation())

    ret = ba.get_ms_method()
    print(ret)
    ba.config(debug=True)
    ba.set_remote(True)
    ba.set_std_graph_mode()
    duration_s = 3
    ret = ba.set_ms_duration(duration_s)
    print(ret)

    ba.config(debug=False)
    ret = ba.isConnectRotation()
    print(ret)
    sample_N, mear_n = ba.get_rotation_info()
    print('rotaion sample_N: {}, mear_n: {}'.format(sample_N, mear_n))
    if sample_N:
        ret = ba.set_rotation_home()
        print(ret)

        for N in range(sample_N):
            for n in range(mear_n):
                ret = ba.set_rotation_pos(N+1,n+1)
                if not ret[0]:
                    print(ret[1])
                    return
                else:
                    print(ret[1])
                    # ba.start_mear()
                    # ret = ba.get_buffered_value()
                    # for r in ret:
                    #     print('Hardness Result: {}'.format(r))
                    time.sleep(1)
        ba.set_rotation_home()
    ba.close()

def go_to_sample(N=0, n=0):
    ba = Digitest()
   
    ba.open("COM5")
    print(ba.isConnectRotation())

    ret = ba.get_ms_method()
    print(ret)
    ba.config(debug=True)
    ba.set_remote(True)

    ba.config(debug=False)
    ret = ba.isConnectRotation()
    print(ret)
    sample_N, mear_n = ba.get_rotation_info()
    print('rotaion sample_N: {}, mear_n: {}'.format(sample_N, mear_n))
    if sample_N:
        ret = ba.set_rotation_pos(N,n)
    ba.close()

def mearsure():
    ba = Digitest()

    def mear(ba):
        ba.start_mear()
        while True:
            statusCode, value = ba.get_single_value()
            print(f'statusCode {statusCode} value {value}')
            if statusCode == 1:
                return value
            elif statusCode < 0:
                print('distance too big when measuring')
                return None
            else:
                time.sleep(0.1)

    
    ba.open("COM3")

    ret = ba.get_ms_method()
    print(ret)
    ba.config(debug=True,wait_cmd = True)
    ba.set_remote(True)
    ba.set_std_mode()
    duration_s = 1
    ret = ba.set_ms_duration(duration_s)
    print(ret)
    ret = mear(ba)
    ba.set_remote(False)
    print('Hardness Result: {}'.format(ret))
    ba.close()

def DigitestTest():
    ba = Digitest()
    ba.open("COM3")
    print(ba.get_mode())
    ba.close()

def GelomatDigitestTest():
    ba = GelomatDigitest()
    ba.open("COM4")
    print(ba.get_dev_name())
    print(ba.get_dev_software_version())
    print(ba.get_mode())
    print(ba.get_lift())
    print(ba.get_method())
    ba.close()

def GelomatDigitestMeasure():
    ba = GelomatDigitest()

    def mear(ba):
        ba.start_mear()
        while True:
            statusCode, value = ba.get_single_value()
            if statusCode == 1:
                return value
            elif statusCode < 0:
                print('distance too big when measuring')
                return None
            else:
                time.sleep(0.1)

    
    ba.open("COM4")
    ba.config(debug=False,wait_cmd = False)
    for i in range(5):
        ret = mear(ba)
        print('Hardness Result: {}'.format(ret))
    ba.close()

if __name__ == '__main__':
    # test_rotation_single_mear()
    # test_rotation_graph_mear()
    mearsure()
    