import time
from threading import Thread
import json

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


@app.route('/chat')
def index():
	global thread
	if thread is None:
		thread = Thread(target=ping)
		thread.start()
	return render_template('chat.html')


@socketio.on('send_message')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')
    socketio.emit('echo', {'echo': 'Server Says: '+text})

def ping():
	while True:
		time.sleep(5)
		comment_dict = {"author": "catmoon", 
                        "body": "test", 
                        "author_flair_css_class": "Heat1", 
                        "comment_id": "qwresdf", 
                        "score": "sdfsafd",
                        "created_utc": "123123123", 
                        "emitted": "true"}
        message = json.dumps({'message': comment_dict,'category':'comment', 'thread': 'asda'})
		socketio.emit('echo', message)

if __name__ == '__main__':
    socketio.run(app)
