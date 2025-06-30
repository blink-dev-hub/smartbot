from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
import logging
from datetime import datetime

# Custom logging handler to stream logs via Socket.IO
class SocketIOHandler(logging.Handler):
    def __init__(self, socketio, event_name='log_stream'):
        super().__init__()
        self.socketio = socketio
        self.event_name = event_name

    def emit(self, record):
        # Format the log record into a dictionary
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': self.format(record) # Use the handler's formatter
        }
        self.socketio.emit(self.event_name, log_entry)

def create_api(bot_instance):
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    logging.getLogger('werkzeug').disabled = True # Disable noisy Flask logs

    # Create the handler to be used by the main application logger
    socket_io_handler = SocketIOHandler(socketio)

    @app.route('/api/status', methods=['GET'])
    def get_status():
        return jsonify(bot_instance.get_status())

    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        logs = bot_instance.db.get_recent_logs(bot_instance.db_conn, limit=100)
        return jsonify([{'timestamp': r[0], 'event_type': r[1], 'details': r[2]} for r in logs])

    @app.route('/api/ott_checks', methods=['GET'])
    def get_ott_checks():
        logs = bot_instance.db.get_recent_logs(bot_instance.db_conn, limit=100)
        ott_checks = [
            {'timestamp': r[0], 'event_type': r[1], 'details': r[2]}
            for r in logs if r[1] == 'ott_check'
        ]
        return jsonify(ott_checks)
    
    @app.route('/api/drm_handshakes', methods=['GET'])
    def get_drm_handshakes():
        logs = bot_instance.db.get_recent_logs(bot_instance.db_conn, limit=100)
        drm_events = [
            {'timestamp': r[0], 'event_type': r[1], 'details': r[2]}
            for r in logs if r[1] == 'drm_handshake'
        ]
        return jsonify(drm_events)

    @app.route('/api/screenshots', methods=['GET'])
    def list_screenshots():
        files = sorted(
            bot_instance.screenshots_dir.glob('*.png'), 
            key=lambda p: p.stat().st_mtime, 
            reverse=True
        )
        return jsonify({'files': [f.name for f in files]})

    @app.route('/screenshots/<path:filename>')
    def serve_screenshot(filename):
        return send_from_directory(bot_instance.screenshots_dir.resolve(), filename)

    @app.route('/api/control/<action>', methods=['POST'])
    def control_bot(action):
        if action == 'pause':
            bot_instance.pause()
        elif action == 'resume':
            bot_instance.resume()
        elif action == 'rotate':
            bot_instance.force_rotate = True
        else:
            return jsonify({'status': 'error', 'message': 'Invalid action'}), 400
        return jsonify({'status': 'success', 'message': f'Action "{action}" triggered'})

    # SocketIO test event
    @socketio.on('ping')
    def handle_ping():
        socketio.emit('pong')

    # Return app, socketio, and the custom log handler
    return app, socketio, socket_io_handler