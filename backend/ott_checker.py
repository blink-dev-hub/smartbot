import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# You can set these from the main script
logger = logging.getLogger('SmartBot')
screenshots_dir = Path('screenshots')

def check_ott(service_name, url, screenshots_dir=screenshots_dir, logger=logger):
    screenshot_path = screenshots_dir / f'shot_{service_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    result = False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            # Try to detect video element (simplified)
            try:
                page.wait_for_selector('video', timeout=15000)
                result = True
            except Exception:
                result = False
            page.screenshot(path=str(screenshot_path))
            browser.close()
        logger.info(f"OTT check for {service_name}: {'PASS' if result else 'FAIL'} | Screenshot: {screenshot_path}")
    except Exception as e:
        logger.error(f"OTT check failed for {service_name}: {e}")
    return result, str(screenshot_path)
