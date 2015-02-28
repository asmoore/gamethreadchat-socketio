import time
from threading import Thread
import json
from datetime import datetime, timedelta
import os
import sys

from flask import Flask, flash, render_template, session, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import praw

from models import *

REDIRECT_URL = os.environ['REDIRECT_URL']
GTC_CLIENT_ID = os.environ['GTC_CLIENT_ID']
GTC_SECRET = os.environ['GTC_SECRET']

r = praw.Reddit('OAuth gamethread chat by /u/catmoon')
r.set_oauth_app_info(GTC_CLIENT_ID, GTC_SECRET, REDIRECT_URL)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
socketio = SocketIO(app)
thread = None

@app.route('/')
def index():
	global thread
	if thread is None:
		thread = Thread(target=ping)
		thread.start()
	return render_template('home.html')


@app.route('/chat')
def chat():
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
		#comment_dict = {"author": "catmoon", 
		#				"body": "test", 
		#				"author_flair_css_class": "Heat1", 
		#				"comment_id": "qwresdf", 
		#				"score": "sdfsafd",
		#				"created_utc": "123123123", 
		#				"emitted": "true"}
		#message = json.dumps({'message': comment_dict,'category':'comment', 'thread': 'asda'})
		#socketio.emit('echo', message)
        today = datetime.today().strftime('%Y%m%d')
        games = db.session.query(Game).filter_by(game_date = today).all()        
        for game in games:
            if game.scoreJSON:
                scoreJSON = json.loads(game.scoreJSON)
                ws.send({'message': scoreJSON, 'category': 'score', 'thread': game.thread_id})
            if game.comments:
                for comment in game.comments:
                    if comment.emitted == "true":
                        pass
                    else:
                        comment.emitted = "true"
                        comment_dict = {"author": comment.author, 
                                     "body": comment.body, 
                                     "author_flair_css_class": comment.author_flair_css_class, 
                                     "comment_id": comment.id, 
                                     "score": comment.score,
                                     "created_utc": comment.created_utc, 
                                     "emitted": "true"}
                        message = json.dumps({'message': comment_dict,'category':'comment', 'thread': 'asda'})
                        ws.send(message)
        db.session.commit()

if __name__ == '__main__':
    socketio.run(app)
