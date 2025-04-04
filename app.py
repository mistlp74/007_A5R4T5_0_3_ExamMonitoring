from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Структура сесій:
# { '123456': { 'teacher': 'Імʼя', 'students': ['Учень1', ...], 'participants': [{'name': 'Anna', 'role': 'student'}] } }
sessions = {}


def generate_session_code():
    return str(random.randint(100000, 999999))


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/choose_role', methods=['POST'])
def choose_role():
    role = request.form.get('role')
    name = request.form.get('name')

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
    session_code = generate_session_code()
    sessions[session_code] = {
        'teacher': teacher_name,
        'students': [],
        'participants': [{'name': teacher_name, 'role': 'teacher'}]
    }
    return redirect(url_for('session', role='teacher', name=teacher_name, code=session_code))


@app.route('/join_session', methods=['POST'])
def join_session():
    user_name = request.form.get('name')
    session_code = request.form.get('session_code')

    if session_code in sessions:
        if user_name == sessions[session_code]['teacher']:
            return redirect(url_for('session', role='teacher', name=user_name, code=session_code))
        else:
            sessions[session_code]['students'].append(user_name)
            sessions[session_code]['participants'].append({'name': user_name, 'role': 'student'})
            return redirect(url_for('session', role='student', name=user_name, code=session_code))
    else:
        return "Сесія не знайдена", 404


@app.route('/session/<role>/<name>/<code>')
def session(role, name, code):
    if code not in sessions:
        return "Сесія не знайдена", 404
    participants = sessions[code]['participants']
    return render_template('session.html', role=role, name=name, session_code=code, participants=participants)


# Коли хтось приєднується — приєднуємо до socket кімнати
@socketio.on('join')
def on_join(data):
    session_code = data['session_code']
    name = data['name']
    join_room(f"{session_code}:{name}")

@socketio.on('video_frame')
def handle_video_frame(data):
    session_code = data['session_code']
    sender = data['sender']
    frame = data['frame']

    # Ретранслюємо лише вчителям з цієї сесії
    for p in sessions[session_code]['participants']:
        if p['role'] == 'teacher' and p['name'] != sender:
            room = f"{session_code}:{p['name']}"
            socketio.emit('receive_frame', {
                'sender': sender,
                'frame': frame
            }, room=room)


# Обробка надсилання повідомлення
@socketio.on('send_message')
def handle_send_message(data):
    session_code = data['session_code']
    sender = data['sender']
    recipient = data['recipient']
    message = data['message']

    room = f"{session_code}:{recipient}"
    emit('receive_message', {
        'sender': sender,
        'message': message
    }, room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
