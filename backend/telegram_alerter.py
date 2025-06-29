import requests
import logging

logger = logging.getLogger('SmartBot')

def send_message(token, chat_id, message):
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Telegram message failed: {response.text}")
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")

def send_photo(token, chat_id, photo_path, caption=""):
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption}
            response = requests.post(url, data=data, files=files, timeout=20)
            if response.status_code != 200:
                logger.warning(f"Telegram photo failed: {response.text}")
    except Exception as e:
        logger.error(f"Telegram send photo failed: {e}") 