import os
import json
import logging
import time
import threading
from pathlib import Path

# Local Modules
from ott_checker import check_ott
import device_manager
import database
import telegram_alerter
from api import create_api

class SmartBot:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('SmartBot')

        # State
        self.is_paused = False
        self.is_safe_mode = False
        self.force_rotate = False
        self.last_known_good_ip = None
        self.retries = 0

        # Paths
        self.screenshots_dir = Path(config['paths'].get('screenshots', 'screenshots'))
        self.ip_cache_path = Path(config['paths'].get('ipcache', 'ip_cache.json'))
        self.db_path = Path(config['paths'].get('database', 'smartbot.db'))
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        if not self.ip_cache_path.exists():
            with open(self.ip_cache_path, 'w') as f:
                json.dump({'good': [], 'bad': []}, f)

        # Modules
        self.db_conn = database.setup_database(self.db_path)
        self.db = database
        self.telegram = telegram_alerter
        # Get the socket handler from the api module
        self.api_app, self.api_socketio, socket_io_handler = create_api(self)
        
        # Pass handler to logging setup
        self.setup_logging(socket_io_handler)

    def setup_logging(self, socket_handler=None):
        # Prevent adding handlers multiple times
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_path = self.config['paths'].get('log', 'smartbot.log')
        
        # Add file and stream handlers
        self.logger.addHandler(logging.FileHandler(log_path))
        self.logger.addHandler(logging.StreamHandler())
        
        # Add the socket handler for live streaming
        if socket_handler:
            socket_handler.setFormatter(formatter)
            self.logger.addHandler(socket_handler)
            
        self.logger.setLevel(logging.INFO)


    def load_ip_cache(self):
        with open(self.ip_cache_path) as f:
            return json.load(f)

    def save_ip_cache(self, cache):
        with open(self.ip_cache_path, 'w') as f:
            json.dump(cache, f, indent=2)

    def add_ip_to_cache(self, ip, status):
        cache = self.load_ip_cache()
        if status == 'good' and ip not in cache['good']:
            cache['good'].append(ip)
            if ip in cache['bad']: cache['bad'].remove(ip)
        elif status == 'bad' and ip not in cache['bad']:
            cache['bad'].append(ip)
            if ip in cache['good']: cache['good'].remove(ip)
        self.save_ip_cache(cache)

    def is_ip_flagged(self, ip):
        return ip in self.load_ip_cache()['bad']

    def score_ott_result(self, passed):
        return 50 if passed else 0
    
    def get_status(self):
        return {
            'is_paused': self.is_paused,
            'is_safe_mode': self.is_safe_mode,
            'current_ip': device_manager.get_current_ip(),
            'last_known_good_ip': self.last_known_good_ip,
            'retries': self.retries,
        }

    def pause(self):
        self.is_paused = True
        self.logger.info("Bot has been paused via API.")
        self.db.log_event(self.db_conn, "control", "Bot paused")

    def resume(self):
        self.is_paused = False
        self.is_safe_mode = False # Resume also exits safe mode
        self.logger.info("Bot has been resumed via API.")
        self.db.log_event(self.db_conn, "control", "Bot resumed")

    def run_api(self):
        host = self.config['api'].get('host', '0.0.0.0')
        port = self.config['api'].get('port', 5000)
        self.api_socketio.run(self.api_app, host=host, port=port)

    def run(self):
        self.db.log_event(self.db_conn, "lifecycle", "SmartBot started")
        self.logger.info("SmartBot Started")
        self.telegram.send_message(
            self.config['telegram']['bot_token'],
            self.config['telegram']['chat_id'],
            "✅ SmartBot Started"
        )
        # Run Flask API in a separate thread
        api_thread = threading.Thread(target=self.run_api, daemon=True)
        api_thread.start()
        
        while True:
            if self.is_paused or self.is_safe_mode:
                self.logger.info("Bot is paused or in safe mode. Sleeping...")
                time.sleep(5)
                continue

            try:
                # 1. Device health check
                if not device_manager.device_health():
                    self.is_safe_mode = True
                    self.logger.error("Device health check failed. Entering SAFE MODE.")
                    self.db.log_event(self.db_conn, "error", "Device health failed")
                    self.telegram.send_message(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], "🚨 Device health failed! Entering SAFE MODE.")
                    continue

                # 2. Get current IP and check if flagged
                current_ip = device_manager.get_current_ip()
                if self.is_ip_flagged(current_ip) or self.force_rotate:
                    self.logger.warning(f"IP {current_ip} is flagged or rotation forced. Rotating...")
                    self.db.log_event(self.db_conn, "rotation", f"IP {current_ip} flagged or rotation forced")
                    current_ip = device_manager.rotate_ip()
                    self.force_rotate = False
                    continue

                # 3. OTT checks
                all_passed = True
                for service, url in self.config.get('ott_services', {}).items():
                    self.logger.info(f"Checking OTT for {service}...")
                    ott_result = check_ott(service, url, self.screenshots_dir, self.logger)
                    
                    passed = ott_result['success']
                    final_screenshot = ott_result['final_screenshot_path']
                    drm_detected = ott_result['drm_handshake_detected']
                    drm_screenshot = ott_result['drm_screenshot_path']

                    score = self.score_ott_result(passed)
                    log_data = {'service': service, 'ip': current_ip, 'passed': passed, 'score': score, 'drm_detected': drm_detected, 'screenshot': final_screenshot}
                    self.db.log_event(self.db_conn, "ott_check", json.dumps(log_data))
                    
                    # Emit events for real-time frontend updates
                    event_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.api_socketio.emit('new_db_log', {'timestamp': event_timestamp, 'event_type': 'ott_check', 'details': json.dumps(log_data)})
                    self.api_socketio.emit('ott_check', {'timestamp': event_timestamp, 'details': log_data})
                    self.api_socketio.emit('new_screenshot', {'filename': Path(final_screenshot).name})

                    # Handle DRM handshake event specifically
                    if drm_detected and drm_screenshot:
                        self.logger.info(f"DRM handshake detected for {service}. Logging and sending alert.")
                        drm_log_data = {'service': service, 'ip': current_ip, 'screenshot': drm_screenshot}
                        self.db.log_event(self.db_conn, "drm_handshake", json.dumps(drm_log_data))
                        
                        # Emit events for real-time frontend updates
                        drm_event_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        self.api_socketio.emit('new_db_log', {'timestamp': drm_event_timestamp, 'event_type': 'drm_handshake', 'details': json.dumps(drm_log_data)})
                        self.api_socketio.emit('drm_handshake', {'timestamp': drm_event_timestamp, 'details': drm_log_data})
                        self.api_socketio.emit('new_screenshot', {'filename': Path(drm_screenshot).name})
                        self.telegram.send_photo(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], drm_screenshot, caption=f"✅ DRM Handshake SUCCESS for {service} on IP {current_ip}")

                    if not passed:
                        all_passed = False
                        self.add_ip_to_cache(current_ip, 'bad')
                        self.telegram.send_photo(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], final_screenshot, caption=f"❌ OTT Check FAILED for {service} on IP {current_ip}")
                    else:
                        self.add_ip_to_cache(current_ip, 'good')
                        self.last_known_good_ip = current_ip
                        device_manager.set_last_known_good_ip(current_ip)
                        # Only send generic success if no specific DRM event was fired
                        if not drm_detected:
                            self.telegram.send_photo(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], final_screenshot, caption=f"✅ OTT Check PASSED for {service} on IP {current_ip}")

                # 4. Rotation logic
                if not all_passed:
                    self.logger.warning(f"IP {current_ip} failed OTT check. Rotating IP.")
                    device_manager.rotate_ip()
                    self.retries += 1
                    if self.retries >= self.config.get('max_retries', 3):
                        self.is_safe_mode = True
                        self.logger.error("Max retries reached. Entering SAFE MODE.")
                        self.db.log_event(self.db_conn, "error", "Max retries reached")
                        self.api_socketio.emit('status_update', self.get_status())
                        self.telegram.send_message(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], "🚨 Max retries reached! Entering SAFE MODE.")
                else:
                    self.retries = 0
                
                self.api_socketio.emit('status_update', self.get_status())
                
                interval = self.config.get('loop_interval_seconds', 300)
                self.logger.info(f"Loop finished. Sleeping for {interval} seconds.")
                time.sleep(interval)

            except Exception as e:
                self.is_safe_mode = True
                self.logger.error(f"Unexpected error: {e}. Entering SAFE MODE.", exc_info=True)
                self.db.log_event(self.db_conn, "error", f"Unexpected error: {e}")
                self.telegram.send_message(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], f"🔥 UNEXPECTED ERROR: {e}. Entering SAFE MODE.")
        
                self.db.log_event(self.db_conn, "lifecycle", "SmartBot stopped")

def main():
    CONFIG_PATH = Path(__file__).parent / 'config.json'
    if not CONFIG_PATH.exists():
        print(f"FATAL: Config file not found at {CONFIG_PATH}")
        return
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    bot = SmartBot(config)
    bot.run()

if __name__ == "__main__":
    main()