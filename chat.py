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


#OAuth2 with reddit 
@app.route("/auth/", methods = ['GET'])
def auth():
	code = request.args.get('code', '')
	info = r.get_access_information(code)
	r.set_access_credentials(**info)
	user = r.get_me()
	session['access_token'] = info['access_token']
	session['refresh_token'] = info['refresh_token']
	session['username'] = user.name
	session['logged_in'] = True    
	return redirect(url_for('home'))


#Home page
@app.route("/", methods = ['GET'])
def home():
	global thread
	if thread is None:
		thread = Thread(target=chat_backend)
		thread.start()
	authorize_url = r.get_authorize_url('DifferentUniqueKey','identity edit submit',refreshable = True)
	today = datetime.today().strftime('%Y%m%d')
	yesterday = (datetime.now()-timedelta(1)).strftime('%Y%m%d')
	gameslist = [];
	#top_users = utils.get_top_users(yesterday)
	#top_scorers = utils.get_top_scorers(yesterday)
	games = db.session.query(Game).filter_by(game_date = today).all()
	for game in games:
		gameslist.append({"game_date": game.game_date, 
					"home_key": game.home_key,
					"visitor_key": game.visitor_key,
					"home_name": game.home_name,
					"visitor_name": game.visitor_name,
					"home_score": game.home_score,
					"visitor_score": game.visitor_score,
					"game_status": game.game_status,
					"game_time": game.game_time,
					"game_location": game.game_location,
					"period_value": game.period_value,
					"game_id": game.id,
					"thread_id": game.thread_id})
	#return render_template("home.html", gameslist = gameslist, authorize_url = authorize_url, top_users = top_users, top_scorers = top_scorers)
	return render_template("home.html", gameslist = gameslist)


@app.route("/chat/<thread_id>/", methods = ['GET'])
def chat(thread_id):
	global thread
	if thread is None:
		thread = Thread(target=chat_backend)
		thread.start()
	return render_template('chat.html',thread_id = thread_id)


@socketio.on('send_message')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')
    socketio.emit('echo', {'echo': 'Server Says: '+text})


def chat_backend():
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
		socketio.emit('echo', message, room='room1')
        #today = datetime.today().strftime('%Y%m%d')
        #games = db.session.query(Game).filter_by(game_date = today).all()        
        #for game in games:
        #    if game.scoreJSON:
        #        scoreJSON = json.loads(game.scoreJSON)
        #        socketio.emit('echo', {'message': scoreJSON, 'category': 'score', 'thread': game.thread_id})
        #    if game.comments:
        #        for comment in game.comments:
        #            if comment.emitted == "true":
        #                pass
        #            else:
        #                comment.emitted = "true"
        #                comment_dict = {"author": comment.author, 
        #                             "body": comment.body, 
        #                             "author_flair_css_class": comment.author_flair_css_class, 
        #                             "comment_id": comment.id, 
        #                             "score": comment.score,
        #                             "created_utc": comment.created_utc, 
        #                             "emitted": "true"}
        #                message = json.dumps({'message': comment_dict,'category':'comment', 'thread': 'asda'})
        #                socketio.emit('echo', message)
        #db.session.commit()

if __name__ == '__main__':
    socketio.run(app)
