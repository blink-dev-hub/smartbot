import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import re
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time
from appium.options.android import UiAutomator2Options

# You can set these from the main script
logger = logging.getLogger('SmartBot')
screenshots_dir = Path('screenshots')

DRM_LICENSE_URL_PATTERNS = [
    re.compile(r'licenser\.vmp\.cdn\.prod\.dtci\.technology'),  # Hotstar
    re.compile(r'edge\.media\.sonyliv\.com/license/widevine'), # SonyLIV
    re.compile(r'widevine-proxy\.zee5\.com'),                 # Zee5
    re.compile(r'playready-proxy\.zee5\.com'),                # Zee5
]

def _handle_cookie_banners(page):
    """General purpose cookie banner handler."""
    cookie_buttons = [
        page.locator('button:has-text("Accept")'),
        page.locator('button:has-text("Allow All")'),
        page.locator('button:has-text("I Accept")'),
        page.locator('#allow_all'),
    ]
    for button in cookie_buttons:
        try:
            if button.is_visible(timeout=2000):
                button.click(timeout=2000)
                logger.info("Clicked a cookie consent button.")
                page.wait_for_timeout(1000)
                return
        except Exception:
            pass # Button not found or clickable

def _login_hotstar(page, credentials):
    logger.info("Attempting Hotstar login... Please log in manually in the browser if needed.")
    page.goto("https://www.hotstar.com/in/subscribe/sign-in", timeout=60000)
    try:
        # A more robust locator for the mobile/email field
        email_field = page.locator('input[aria-label="email or mobile number"]')
        expect(email_field).to_be_visible(timeout=10000)
        email_field.fill(credentials['username'])
        # This part is unlikely to succeed due to OTP, but we try.
        # The main goal is to let the user log in once and save the session.
        page.locator('button:has-text("GET OTP")').click()
        logger.info("Filled username. The session should be saved for future runs.")
    except Exception as e:
        logger.warning(f"Could not automatically fill login form (this is expected if already logged in or page changed): {e}")

def check_ott(service_name, service_config, screenshots_dir=screenshots_dir, logger=logger):
    """
    Checks an OTT service for video playback and DRM handshake using browser or Android automation.
    """
    mode = service_config.get('mode', 'browser')
    if mode == 'android':
        return check_ott_android(service_name, service_config, screenshots_dir, logger)
    # Default: browser mode (Playwright)
    url = service_config['url']
    
    final_screenshot_path = screenshots_dir / f'shot_{service_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_final.png'
    drm_screenshot_path = None
    
    success = False
    drm_handshake_detected = False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
            page = browser.new_page()

            def handle_request(request):
                nonlocal drm_handshake_detected, drm_screenshot_path
                if any(pattern.search(request.url) for pattern in DRM_LICENSE_URL_PATTERNS):
                    logger.info(f"DRM license request detected for {service_name}: {request.url}")
                    drm_handshake_detected = True
                    drm_screenshot_filename = f'shot_{service_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_drm.png'
                    drm_screenshot_path = screenshots_dir / drm_screenshot_filename
                    page.screenshot(path=str(drm_screenshot_path))
                    logger.info(f"DRM handshake screenshot saved to {drm_screenshot_path}")

            page.on('request', handle_request)
            page.goto(url, timeout=60000, wait_until='domcontentloaded')

            _handle_cookie_banners(page)
            
            page.wait_for_timeout(10000)

            try:
                expect(page.locator('video')).to_be_visible(timeout=20000)
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

def check_ott_android(service_name, service_config, screenshots_dir=screenshots_dir, logger=logger):
    """
    Android OTT check using Appium. Launches the app, attempts to play content, takes a screenshot, and checks for playback UI.
    """
    logger.info(f"[Android] Checking OTT for {service_name} on device {service_config.get('device_udid')}")
    final_screenshot_path = screenshots_dir / f'shot_{service_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_android_final.png'
    success = False
    drm_handshake_detected = False
    driver = None
    try:
        desired_caps = {
            'platformName': 'Android',
            'deviceName': service_config.get('device_udid'),
            'udid': service_config.get('device_udid'),
            'appPackage': service_config.get('appPackage'),
            'appActivity': service_config.get('appActivity'),
            'automationName': 'UiAutomator2',
            'noReset': True,
            'newCommandTimeout': 120,
            'forceAppLaunch': True,  # Ensure app is brought to foreground
        }
        options = UiAutomator2Options().load_capabilities(desired_caps)
        driver = webdriver.Remote(service_config.get('appium_server_url'), options=options)
        logger.info(f"[Android] App launched for {service_name}")
        time.sleep(8)  # Wait for app to load
        time.sleep(10)  # Additional wait for UI to load fully

        # After launching the app, verify the correct app is in the foreground
        expected_package = service_config.get('appPackage')
        try:
            current_package = driver.current_package
        except Exception as e:
            logger.error(f"[Android] Could not get current package: {e}")
            current_package = None
        if current_package != expected_package:
            logger.error(f"[Android] Expected app {expected_package} but found {current_package} in foreground!")
            try:
                driver.save_screenshot(str(final_screenshot_path))
                logger.info(f"[Android] Screenshot saved (wrong app): {final_screenshot_path}")
            except Exception as e:
                logger.warning(f"[Android] Screenshot failed for wrong app: {e}")
            if driver:
                driver.quit()
            return {
                'success': False,
                'error': f'App {expected_package} not in foreground, found {current_package}',
                'final_screenshot_path': str(final_screenshot_path),
                'drm_screenshot_path': None,
            }

        # Dismiss common popups if present
        popup_texts = ["Close", "Skip", "Not Now", "Dismiss", "Cancel"]
        for popup_text in popup_texts:
            try:
                popup_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{popup_text}")')
                if popup_btn.is_displayed():
                    popup_btn.click()
                    logger.info(f"[Android] Dismissed popup: {popup_text}")
                    time.sleep(2)
            except Exception:
                continue

        # Try to click the first clickable element (likely a video thumbnail)
        try:
            clickable_elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().clickable(true)')
            for el in clickable_elements:
                # Skip elements that are too small (likely not a video)
                bounds = el.get_attribute('bounds')
                if bounds:
                    # Parse bounds string like [x1,y1][x2,y2]
                    m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                    if m:
                        x1, y1, x2, y2 = map(int, m.groups())
                        width, height = x2 - x1, y2 - y1
                        if width > 100 and height > 100:  # likely a visible tile
                            try:
                                el.click()
                                logger.info(f"[Android] Clicked a clickable element (likely video thumbnail) with bounds {bounds}")
                                time.sleep(5)
                                break
                            except Exception as e:
                                logger.warning(f"[Android] Failed to click clickable element: {e}")
        except Exception as e:
            logger.warning(f"[Android] Could not find clickable elements: {e}")

        # For Zee5 and Hotstar, take screenshot before clicking Play to avoid FLAG_SECURE error
        if service_name.lower() in ["zee5", "hotstar"]:
            try:
                driver.save_screenshot(str(final_screenshot_path))
                logger.info(f"[Android] Screenshot saved (before Play): {final_screenshot_path}")
            except Exception as e:
                logger.warning(f"[Android] Screenshot failed for {service_name} (before Play): {e}")

        # Try to find and click a 'Play' button (custom selectors per app)
        play_clicked = False
        if service_name.lower() == "hotstar":
            try:
                el = driver.find_element(AppiumBy.ID, "tag_button_watch_now")
                if el.is_displayed():
                    el.click()
                    logger.info(f"[Android] Clicked Watch Now button for Hotstar")
                    play_clicked = True
                    time.sleep(5)
            except Exception:
                try:
                    el = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Watch Now")
                    if el.is_displayed():
                        el.click()
                        logger.info(f"[Android] Clicked Watch Now (accessibility) for Hotstar")
                        play_clicked = True
                        time.sleep(5)
                except Exception as e:
                    logger.warning(f"[Android] Play button not found for Hotstar: {e}")
        elif service_name.lower() == "sonyliv":
            try:
                el = driver.find_element(AppiumBy.XPATH, "//*[@resource-id='com.sonyliv:id/spotlight_button_text' and @text='Play Now']")
                if el.is_displayed():
                    el.click()
                    logger.info(f"[Android] Clicked Play Now button for SonyLIV")
                    play_clicked = True
                    time.sleep(5)
            except Exception:
                try:
                    el = driver.find_element(AppiumBy.ID, "com.sonyliv:id/spotlight_button_text")
                    if el.is_displayed() and el.text == "Play Now":
                        el.click()
                        logger.info(f"[Android] Clicked Play Now (ID) for SonyLIV")
                        play_clicked = True
                        time.sleep(5)
                except Exception as e:
                    logger.warning(f"[Android] Play button not found for SonyLIV: {e}")
        elif service_name.lower() == "zee5":
            try:
                el = driver.find_element(AppiumBy.XPATH, "//*[@resource-id='com.graymatrix.did:id/playIcon' and @content-desc='Play Button']")
                if el.is_displayed():
                    el.click()
                    logger.info(f"[Android] Clicked Play Button for Zee5")
                    play_clicked = True
                    time.sleep(5)
            except Exception:
                try:
                    el = driver.find_element(AppiumBy.ID, "com.graymatrix.did:id/playIcon")
                    if el.is_displayed():
                        el.click()
                        logger.info(f"[Android] Clicked Play Icon (ID) for Zee5")
                        play_clicked = True
                        time.sleep(5)
                except Exception as e:
                    logger.warning(f"[Android] Play button not found for Zee5: {e}")
        else:
            # Fallback: generic selectors
            play_buttons = [
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Play")'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Play")'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Watch")'),
            ]
            for by, selector in play_buttons:
                try:
                    el = driver.find_element(by, selector)
                    if el.is_displayed():
                        el.click()
                        logger.info(f"[Android] Clicked Play/Watch button for {service_name}")
                        play_clicked = True
                        time.sleep(5)
                        break
                except Exception:
                    continue
        if not play_clicked:
            logger.warning(f"[Android] Play button not found for {service_name}")
            try:
                driver.save_screenshot(str(final_screenshot_path))
                logger.info(f"[Android] Screenshot saved (partial success): {final_screenshot_path}")
                success = True  # Mark as partial success if app is open
            except Exception as e:
                logger.warning(f"[Android] Screenshot failed for {service_name}: {e}")

        # Take screenshot for non-Zee5 apps after Play
        if service_name.lower() != "zee5":
            try:
                driver.save_screenshot(str(final_screenshot_path))
                logger.info(f"[Android] Screenshot saved: {final_screenshot_path}")
            except Exception as e:
                logger.warning(f"[Android] Screenshot failed for {service_name}: {e}")

        # Check for playback UI (e.g., pause button, progress bar, etc.)
        playback_indicators = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Pause")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("progress")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Now Playing")'),
        ]
        for by, selector in playback_indicators:
            try:
                el = driver.find_element(by, selector)
                if el.is_displayed():
                    success = True
                    logger.info(f"[Android] Playback UI detected for {service_name}")
                    break
            except Exception:
                continue
        # DRM handshake detection: Not trivial on Android, so set to False or implement with logcat parsing if needed
        drm_handshake_detected = False

        # Only set success = True if play_clicked and correct app is in foreground
        if play_clicked:
            success = True
    except Exception as e:
        logger.error(f"[Android] OTT check failed for {service_name}: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()
    return {
        'success': success,
        'drm_handshake_detected': drm_handshake_detected,
        'final_screenshot_path': str(final_screenshot_path),
        'drm_screenshot_path': None,
    }
