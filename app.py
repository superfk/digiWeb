from backend import creat_app
from flask_socketio import SocketIO, emit
from backend.corelib.hardwarelib.digitest import Digitest
import time

app = creat_app()
socketio = SocketIO(app,  cors_allowed_origins=['http://localhost:9031', 'https://localhost:9031'])

class DigiTestTester:
    def mear(self):
        ba = Digitest()
        ba.open("COM5")
        def mearsure(ba):
            ba.start_mear()
            while True:
                statusCode, value = ba.get_single_value()
                print(f'statusCode {statusCode} value {value}')
                if value != '"DEVICE BUSY"':
                    return value
                elif statusCode < 0:
                    print('distance too big when measuring')
                    return None
                else:
                    time.sleep(1)
        ret = ba.get_ms_method()
        print(ret)
        ba.config(debug=False,wait_cmd = True)
        ba.set_remote(True)
        ret = mearsure(ba)
        print('Hardness Result: {}'.format(ret))
        ba.set_remote(False)
        ba.close()
        return ret

class MainTask:
    def __init__(self) -> None:
        self.batchName = ''
        self.historyData = []
    
    def reset_batch(self, batchName):
        self.batchName = batchName
        self.historyData = []
    
    def mear(self):
        value = DigiTestTester().mear()
        self.historyData.append(value)    
        return value    
    
    def show_records(self):
        return self.historyData

mainTask = MainTask()

@socketio.on('client_event')
def echo(msg):
    print(msg)
    emit('server_response', msg)

@socketio.on('connect')
def connect():
    print('client connected')
    emit('server_sent_connect_ok', 'Hi from Server')
    
@socketio.on('init_batch')
def init_batch(batchName):
    mainTask.reset_batch(batchName)

@socketio.on('mear')
def mear():
    data = mainTask.mear()
    emit('send_mear_data', data, broadcast=True)
    data = mainTask.show_records()
    emit('show_records', data, broadcast=True)

@socketio.on('show_records')
def show_records():
    data = mainTask.show_records()
    emit('show_records', data, broadcast=True)

def test():
    data = DigiTestTester().mear()
    print(data)

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=9031,  keyfile='key.pem', certfile='cert.pem')
    # test()