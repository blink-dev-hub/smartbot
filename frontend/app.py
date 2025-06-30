from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SMARTBOT_SECRET_KEY', 'a-very-secret-key')

# --- User Auth Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirect to /login if not authenticated

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password = password_hash

# For demo, using an in-memory user store. In production, use a database.
users = {
    "1": User(id="1", username="vladislav", password_hash=generate_password_hash("smartbot"))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# --- Backend API Proxy ---
BACKEND_API = 'http://localhost:5000'

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_to_login = next((u for u in users.values() if u.username == username), None)
        
        if user_to_login and check_password_hash(user_to_login.password, password):
            login_user(user_to_login)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- API proxy routes ---
@app.route('/api/status')
@login_required
def api_status():
    try:
        r = requests.get(f'{BACKEND_API}/api/status', timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
@login_required
def api_logs():
    try:
        r = requests.get(f'{BACKEND_API}/api/logs', timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ott_checks')
@login_required
def api_ott_checks():
    try:
        r = requests.get(f'{BACKEND_API}/api/ott_checks', timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/drm_handshakes')
@login_required
def api_drm_handshakes():
    try:
        r = requests.get(f'{BACKEND_API}/api/drm_handshakes', timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/screenshots')
@login_required
def api_screenshots():
    try:
        r = requests.get(f'{BACKEND_API}/api/screenshots', timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/screenshots/<path:filename>')
@login_required
def serve_screenshot_from_backend(filename):
    try:
        resp = requests.get(f'{BACKEND_API}/screenshots/{filename}', stream=True, timeout=10)
        resp.raise_for_status()
        return resp.raw.read(), resp.status_code, resp.headers.items()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/control/<action>', methods=['POST'])
@login_required
def api_control(action):
    try:
        r = requests.post(f'{BACKEND_API}/api/control/{action}', timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=80)