from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import math
import time
import random
import pip
pip.main(['install','mysql-connector-python-rf'])
import mysql.connector       
import configparser as ConfigParser
import serial
async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

config = ConfigParser.ConfigParser()

config = {
  'user': 'lukrecia',
  'password': 'lukrecia',
  'host': 'localhost',
  'database': 'zadanie',
  'raise_on_warnings': True
}



#ser = serial.Serial("/dev/ttyUSB0", 9600)
#ser.baudrate = 9600

def background_thread(args):

    ser = serial.Serial("/dev/ttyUSB0", 9600)
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    tab = 'DELETE FROM `data`;'
    cursor.execute(tab)
    cnx.commit()

    count = 0
    dataCount = 0
    dataList = []

    while(1):
        add = "INSERT INTO data (Hodnota) VALUES (%s)"
        data = ser.readline()
        
        data = str(data.strip(), 'UTF-8')
        print(data)
        cursor.execute(add, (int(data),))
        cnx.commit()
        if args:
            A = dict(args).get('A')
            btnV = dict(args).get('btn_value')
        else:
            A = 1
            btnV = 'null'
        
        btnV = dict(args).get('btn_value')
        print(args)  
        socketio.sleep(2)
        count += 1
        dataCount += 1

        dataDict = {
          "x": dataCount,
          "y": data,
          }

        socketio.emit('my_response',
                    {'data': float(data), 'count': count},
                      namespace='/test') 
    

@app.route('/')
def hello():
    return render_template('indexz.html')

@app.route('/indexz', methods=['GET', 'POST'])
def graphlive():
    return render_template('indexz.html', async_mode=socketio.async_mode)

@socketio.on('my_event', namespace='/test')
def test_message(message):   
#    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
#    emit('my_response',
#         {'data': message['value'], 'count': session['receive_count']})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
#    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']    

@socketio.on('slider_event', namespace='/test')
def slider_message(message):  
    #print(message['value'])   
    session['slider_value'] = message['value']  

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=81, debug=True)
