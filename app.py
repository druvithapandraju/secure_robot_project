from flask import Flask, render_template, request, redirect, session, Response, jsonify
from config import SECRET_KEY
from database.db import init_db, get_user, log_event, get_logs
from werkzeug.security import check_password_hash
from models.vision import start_camera, process_frame, load_known_faces
from services.alert import send_alert

app = Flask(__name__)
app.secret_key = SECRET_KEY

init_db()
load_known_faces()

status_global = "Monitoring..."

@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    user = get_user(request.form['username'])

    if user and check_password_hash(user[1], request.form['password']):
        session['user'] = user[0]
        start_camera()
        return redirect('/dashboard')

    return "Invalid login"


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html')


def generate_frames():
    global status_global

    while True:
        frame, status, unknown = process_frame()

        if frame is None:
            break

        status_global = status

        if unknown:
            send_alert(status)
            log_event(status)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video')
def video():
    if 'user' not in session:
        return redirect('/')
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def status():
    return jsonify({"status": status_global})


@app.route('/logs')
def logs():
    return jsonify(get_logs())


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
