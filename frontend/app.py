from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SMARTBOT_SECRET_KEY', 'supersecretkey')  # Change in production

USERNAME = 'vladislav'
PASSWORD = 'smartbot'

BACKEND_API = 'http://localhost:5000'  # Change if backend runs elsewhere

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/frontend_api/status')
def frontend_status():
    try:
        r = requests.get(f'{BACKEND_API}/api/status', timeout=3)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/frontend_api/logs')
def frontend_logs():
    try:
        r = requests.get(f'{BACKEND_API}/api/logs', timeout=3)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/frontend_api/screenshots')
def frontend_screenshots():
    # List screenshot files from backend/screenshots/
    screenshots_dir = os.path.join(os.path.dirname(__file__), '../backend/screenshots')
    files = [f for f in os.listdir(screenshots_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    files.sort(reverse=True)
    return jsonify({'files': files})

@app.route('/frontend_api/screenshot/<filename>')
def frontend_screenshot_file(filename):
    # Proxy screenshot file from backend
    screenshots_dir = os.path.join(os.path.dirname(__file__), '../backend/screenshots')
    return send_file(os.path.join(screenshots_dir, filename))

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5001)
