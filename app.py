import threading
import time
import logging
import os
import random
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from cy_frame import process_frame

log_filename = 'server.log'
if os.path.exists(log_filename):
    with open(log_filename, 'w'):
        pass

logging.basicConfig(
    filename=log_filename,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)
app = Flask(__name__)
socketio = SocketIO(app)
sessions = {}
VIOLATION_COOLDOWN = 5
last_violation_time = {}
last_detection_check = {}
FRAME_CHECK_INTERVAL = 1.0

def generate_session_code():
    return str(random.randint(100000, 999999))
@app.route('/')
def index():
    return render_template('login.html')
@app.route('/choose_role', methods=['POST'])
def choose_role():
    role = request.form.get('role')
    name = request.form.get('name')
    logging.info(f"User's: {role}, name: {name}")
    if role == 'teacher':
        return redirect(url_for('teacher_dashboard', name=name))
    elif role == 'student':
        return redirect(url_for('student_dashboard', name=name))
@app.route('/teacher_dashboard/<name>')
def teacher_dashboard(name):
    return render_template('teacher_dashboard.html', name=name)
@app.route('/student_dashboard/<name>')
def student_dashboard(name):
    return render_template('student_dashboard.html', name=name)
@app.route('/create_session', methods=['POST'])
def create_session():
    teacher_name = request.form.get('name')
    code = generate_session_code()
    sessions[code] = {
        'teacher': teacher_name,
        'students': [],
        'participants': [{'name': teacher_name, 'role': 'teacher'}]
    }
    logging.info(f"session created by {code} teacher {teacher_name}")
    return redirect(url_for('session', role='teacher', name=teacher_name, code=code))
@app.route('/join_session', methods=['POST'])
def join_session():
    name = request.form.get('name')
    code = request.form.get('session_code')
    if code in sessions:
        if name == sessions[code]['teacher']:
            logging.info(f"Teacher {name} joined the session {code}")
            return redirect(url_for('session', role='teacher', name=name, code=code))
        else:
            sessions[code]['students'].append(name)
            sessions[code]['participants'].append({'name': name, 'role': 'student'})
            logging.info(f"Student {name} joined {code}")
            return redirect(url_for('session', role='student', name=name, code=code))
    logging.warning(f"try to join to not existing session: {code}")
    return "Session not found", 404
@app.route('/session/<role>/<name>/<code>')
def session(role, name, code):
    if code not in sessions:
        logging.warning(f"try to join to not existing session: {code}")
        return "Session not found", 404
    participants = sessions[code]['participants']
    return render_template('session.html', role=role, name=name, session_code=code, participants=participants)

@socketio.on('join')
def on_join(data):
    join_room(f"{data['session_code']}:{data['name']}")
    logging.info(f"{data['name']} joined session {data['session_code']}:{data['name']}")

@socketio.on('send_message')
def handle_send_message(data):
    room = f"{data['session_code']}:{data['recipient']}"
    logging.info(f"Messege from {data['sender']} to {data['recipient']}: {data['message']}")
    emit('receive_message', {
        'sender': data['sender'],
        'message': data['message']
    }, room=room)

@socketio.on('video_frame')
def handle_video_frame(data):

    def process_and_send_frame():
        key = f"{data['session_code']}:{data['sender']}"
        now = time.time()
        should_check = (now - last_detection_check.get(key, 0)) > FRAME_CHECK_INTERVAL

        if should_check:
            last_detection_check[key] = now
            try:
                is_face_detected = process_frame(data['frame'])
            except Exception as e:
                logging.error(f"Camera processing Error {data['sender']}: {e}")
                return

            if not is_face_detected:
                if last_violation_time.get(key, 0) + VIOLATION_COOLDOWN < now:
                    last_violation_time[key] = now
                    violation_message = f"No face detected for {data['sender']}"
                    logging.warning(f"[VIOLATION] {violation_message}")

                    room = f"{data['session_code']}:{data['sender']}"
                    socketio.emit('receive_message', {
                        'sender': 'System',
                        'message': violation_message
                    }, room=room)

                    for p in sessions[data['session_code']]['participants']:
                        if p['role'] == 'teacher' and p['name'] != data['sender']:
                            room = f"{data['session_code']}:{p['name']}"
                            socketio.emit('receive_message', {
                                'sender': 'System',
                                'message': violation_message
                            }, room=room)

        for p in sessions[data['session_code']]['participants']:
            if p['role'] == 'teacher' and p['name'] != data['sender']:
                room = f"{data['session_code']}:{p['name']}"
                socketio.emit('receive_frame', {
                    'sender': data['sender'],
                    'frame': data['frame']
                }, room=room)

    thread = threading.Thread(target=process_and_send_frame)
    thread.start()

if __name__ == '__main__':
    logging.info("Server started")
    #socketio.run(app, host='0.0.0.0', port=5000)
    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)

#http://localhost:5000