from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')
    socketio.emit('echo', {'echo': 'Server Says: '+text})

@app.route('/echo')
def ping():
	while True:
		time.sleep(5)
	    socketio.emit('echo', {'echo': 'Server Says: test!'})

if __name__ == '__main__':
    socketio.run(app)
