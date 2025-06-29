from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
import logging

def create_api(bot_instance):
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    logging.getLogger('werkzeug').disabled = True # Disable noisy Flask logs

    @app.route('/api/status', methods=['GET'])
    def get_status():
        return jsonify(bot_instance.get_status())

    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        logs = bot_instance.db.get_recent_logs(bot_instance.db_conn, limit=100)
        return jsonify([{'timestamp': r[0], 'event_type': r[1], 'details': r[2]} for r in logs])
    
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

    # Return both app and socketio
    return app, socketio 