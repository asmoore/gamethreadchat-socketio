import time
from threading import Thread

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None

@app.route('/')
def index():
	global thread
	if thread is None:
		thread = Thread(target=ping)
		thread.start()
	return render_template('index.html')

@socketio.on('send_message')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')
    socketio.emit('echo', {'echo': 'Server Says: '+text})

def ping():
	while True:
		time.sleep(5)
		socketio.emit('echo', {'echo': 'Server Says: test!'})

if __name__ == '__main__':
    socketio.run(app)
