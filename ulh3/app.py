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



ser = serial.Serial("/dev/ttyUSB0", 9600)
#ser.baudrate = 9600

def background_thread(args):

    #ser = serial.Serial("/dev/ttyUSB0", 9600)
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    #tab = 'DELETE FROM `data`;'
    #cursor.execute(tab)
    #cnx.commit()

    count = 0
    dataCount = 0
    dataList = []

    while(1):

        data = ser.readline()
        
        data = str(data.strip(), 'UTF-8')
        #print(data)

        if args:
            A = dict(args).get('A')
            btnV = dict(args).get('btn_value')
        else:
            A = 1
            btnV = 'nieco'
        
        btnV = dict(args).get('btn_value')
        print(args)
 
        #socketio.sleep(2)
        count += 1
        dataCount += 1
    

        if btnV == 1:

            socketio.emit('my_response',
                    {'data': int(data), 'count': count},
                    namespace='/test')

            dataDict = {
                "x": dataCount,
                "y": data,
            }
            dataList.append(dataDict)

        elif btnV == 0 :
            x = str(dataList).replace("'","\"")

            if len(dataList) > 0 :
                add = "INSERT INTO data1 (Hodnota) VALUES (%s)"
                cursor.execute(add, (x,))
                cnx.commit()

                fo = open("static/file/output.txt","a+")
                fo.write("%s\r\n" %x)
                fo.close()

            dataList = []

    

@app.route('/')
def hello():
    return render_template('indexz.html')

@app.route('/indexz', methods=['GET', 'POST'])
def graphlive():
    return render_template('indexz.html', async_mode=socketio.async_mode)

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    print(num)
    cursor.execute("SELECT Hodnota FROM  data1 WHERE id=%s", (num,))
    rv = cursor.fetchone()
    return str(rv[0])

@app.route('/read/<string:num>', methods=['GET', 'POST'])
def readmyfile(num):
    fo = open("static/file/output.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['A'] = message['value']   
    ser.write(str(message['value']).encode()) 

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


@socketio.on('click_eventStart', namespace='/test')
def db_message(message):   
    session['btn_value'] = 1

@socketio.on('click_eventStop', namespace='/test')
def db_message(message):   
    session['btn_value'] = 0

@socketio.on('slider_event', namespace='/test')
def slider_message(message):  
    #print(message['value'])   
    session['slider_value'] = message['value']  

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=82, debug=False)