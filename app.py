from backend import creat_app
from flask_socketio import SocketIO, emit

app = creat_app()
socketio = SocketIO(app)

@socketio.on('client_event')
def echo(msg):
    print(msg)
    emit('server_response', msg)

@socketio.on('connect_event')
def connected_msg(msg):
    emit('server_response', "Hello")

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=8080)
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)