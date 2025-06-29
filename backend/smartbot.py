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
        self.setup_logging()

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
        self.api_app, self.api_socketio = create_api(self)

    def setup_logging(self):
        log_path = self.config['paths'].get('log', 'smartbot.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )

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
        return 100 if passed else 0
    
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
                    passed, screenshot = check_ott(service, url, self.screenshots_dir, self.logger)
                    score = self.score_ott_result(passed)
                    log_data = {'service': service, 'ip': current_ip, 'passed': passed, 'score': score}
                    self.db.log_event(self.db_conn, "ott_check", json.dumps(log_data))
                    self.api_socketio.emit('ott_check', {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'event_type': 'ott_check', 'details': log_data})
                    self.api_socketio.emit('log', {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'event_type': 'ott_check', 'details': log_data})
                    
                    if not passed:
                        all_passed = False
                        self.add_ip_to_cache(current_ip, 'bad')
                        self.telegram.send_photo(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], screenshot, caption=f"❌ OTT Check FAILED for {service} on IP {current_ip}")
                    else:
                        self.add_ip_to_cache(current_ip, 'good')
                        self.last_known_good_ip = current_ip
                        device_manager.set_last_known_good_ip(current_ip)

                # 4. Rotation logic
                if not all_passed:
                    self.logger.warning(f"IP {current_ip} failed OTT check. Rotating IP.")
                    device_manager.rotate_ip()
                    self.retries += 1
                    if self.retries >= self.config.get('max_retries', 3):
                        self.is_safe_mode = True
                        self.logger.error("Max retries reached. Entering SAFE MODE.")
                        self.db.log_event(self.db_conn, "error", "Max retries reached")
                        self.api_socketio.emit('log', {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'event_type': 'error', 'details': 'Max retries reached'})
                        self.api_socketio.emit('status_update', self.get_status())
                        self.telegram.send_message(self.config['telegram']['bot_token'], self.config['telegram']['chat_id'], "🚨 Max retries reached! Entering SAFE MODE.")
                else:
                    self.retries = 0
                # Emit status update after each loop
                self.api_socketio.emit('status_update', self.get_status())
                
                time.sleep(self.config.get('loop_interval_seconds', 300))

            except Exception as e:
                self.is_safe_mode = True
                self.logger.error(f"Unexpected error: {e}. Entering SAFE MODE.")
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