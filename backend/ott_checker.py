import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import re

# You can set these from the main script
logger = logging.getLogger('SmartBot')
screenshots_dir = Path('screenshots')

DRM_LICENSE_URL_PATTERNS = [
    re.compile(r'licenser\.vmp\.cdn\.prod\.dtci\.technology'),  # Hotstar
    re.compile(r'edge\.media\.sonyliv\.com/license/widevine'), # SonyLIV
    re.compile(r'widevine-proxy\.zee5\.com'),                 # Zee5
    re.compile(r'playready-proxy\.zee5\.com'),                # Zee5
]

def check_ott(service_name, url, screenshots_dir=screenshots_dir, logger=logger):
    """
    Checks an OTT service for video playback and DRM handshake.
    
    Returns a dictionary with:
    - success (bool): If the video element was found.
    - drm_handshake_detected (bool): If a DRM license request was detected.
    - final_screenshot_path (str): Path to the final screenshot.
    - drm_screenshot_path (str | None): Path to the screenshot taken when DRM was detected.
    """
    final_screenshot_path = screenshots_dir / f'shot_{service_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_final.png'
    drm_screenshot_path = None
    
    success = False
    drm_handshake_detected = False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def handle_request(request):
                nonlocal drm_handshake_detected, drm_screenshot_path
                if any(pattern.search(request.url) for pattern in DRM_LICENSE_URL_PATTERNS):
                    logger.info(f"DRM license request detected for {service_name}: {request.url}")
                    drm_handshake_detected = True
                    # Take a screenshot when DRM is detected
                    drm_screenshot_filename = f'shot_{service_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_drm.png'
                    drm_screenshot_path = screenshots_dir / drm_screenshot_filename
                    page.screenshot(path=str(drm_screenshot_path))
                    logger.info(f"DRM handshake screenshot saved to {drm_screenshot_path}")

            page.on('request', handle_request)

            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            
            # Wait for a bit to let the player load
            page.wait_for_timeout(10000)

            try:
                page.wait_for_selector('video', timeout=20000)
                success = True
                logger.info(f"Video element found for {service_name}.")
            except Exception:
                success = False
                logger.warning(f"Video element not found for {service_name}.")

            page.screenshot(path=str(final_screenshot_path))
            browser.close()

        logger.info(f"OTT check for {service_name}: {'PASS' if success else 'FAIL'} | DRM detected: {drm_handshake_detected} | Screenshot: {final_screenshot_path}")

    except Exception as e:
        logger.error(f"OTT check failed for {service_name}: {e}", exc_info=True)

    return {
        'success': success,
        'drm_handshake_detected': drm_handshake_detected,
        'final_screenshot_path': str(final_screenshot_path),
        'drm_screenshot_path': str(drm_screenshot_path) if drm_screenshot_path else None,
    }
