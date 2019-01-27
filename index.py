#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os
from datetime import timedelta
from flask import Flask,request,make_response,jsonify,render_template,session,redirect,url_for
from functools import wraps
import src.utils.Utils as Utils
import base64
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # 设置session的保存时间。


socketio = SocketIO(app)



def checkLogin(f):
    @wraps(f)
    def fn(*args, **kwargs):
        if session.get('account') == None: 
            return redirect('/login')
        return f(*args, **kwargs)
    return fn

@app.route('/')
@checkLogin
def index():
    return render_template('index.html',account=session['account'])

@app.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        session['account'] = request.form.get('account')
        return redirect('/')

@socketio.on('connect', namespace='/chat')
def connect():
    emit('connected', {'account': session['account']}, broadcast=True)

@socketio.on('message', namespace='/chat')
def message(data):
    data['account'] = session['account']
    emit('message', data, broadcast=True)

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('disconnect ')


socketio.run(app,debug=True,host='0.0.0.0',port=5000)


