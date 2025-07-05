#!/usr/bin/env python3
"""
Comprehensive system test for SmartBot
"""

import subprocess
import requests
import json
import time
import os

def run_command(command):
    """Run command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_device_connection():
    """Test Android device connection"""
    print("🔍 Testing Android device connection...")
    success, output, error = run_command("adb devices")
    if success and "8b9abf39" in output:
        print("   ✅ Device connected")
        return True
    else:
        print("   ❌ Device not connected")
        return False

def test_appium_server():
    """Test Appium server"""
    print("🔍 Testing Appium server...")
    success, output, error = run_command("curl -s http://localhost:4723/status")
    if success and "ready" in output.lower():
        print("   ✅ Appium server running")
        return True
    else:
        print("   ❌ Appium server not running")
        return False

def test_smartbot_api():
    """Test SmartBot API"""
    print("🔍 Testing SmartBot API...")
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ SmartBot API responding")
            return True
        else:
            print("   ❌ SmartBot API not responding")
            return False
    except Exception as e:
        print(f"   ❌ SmartBot API error: {e}")
        return False

def test_web_dashboard():
    """Test web dashboard"""
    print("🔍 Testing web dashboard...")
    try:
        response = requests.get("http://localhost:80", timeout=5)
        if response.status_code == 200:
            print("   ✅ Web dashboard accessible")
            return True
        else:
            print("   ❌ Web dashboard not accessible")
            return False
    except Exception as e:
        print(f"   ❌ Web dashboard error: {e}")
        return False

def test_ott_services():
    """Test OTT service configuration"""
    print("🔍 Testing OTT service configuration...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        services = config.get('ott_services', {})
        if 'hotstar' in services and 'sonyliv' in services and 'zee5' in services:
            print("   ✅ All OTT services configured")
            return True
        else:
            print("   ❌ Missing OTT service configuration")
            return False
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def test_telegram_config():
    """Test Telegram configuration"""
    print("🔍 Testing Telegram configuration...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        telegram = config.get('telegram', {})
        if telegram.get('bot_token') and telegram.get('chat_id'):
            print("   ✅ Telegram configured")
            return True
        else:
            print("   ⚠️ Telegram not configured (optional)")
            return True
    except Exception as e:
        print(f"   ❌ Telegram config error: {e}")
        return False

def test_file_permissions():
    """Test file permissions"""
    print("🔍 Testing file permissions...")
    files_to_check = ['smartbot.py', 'config.json', 'requirements.txt']
    all_good = True
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ {file} exists")
        else:
            print(f"   ❌ {file} missing")
            all_good = False
    
    return all_good

def test_dependencies():
    """Test Python dependencies"""
    print("🔍 Testing Python dependencies...")
    try:
        import flask
        import playwright
        import appium
        print("   ✅ All dependencies available")
        return True
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        return False

def main():
    print("🧪 SmartBot System Test")
    print("=" * 50)
    
    tests = [
        ("File Permissions", test_file_permissions),
        ("Dependencies", test_dependencies),
        ("OTT Configuration", test_ott_services),
        ("Telegram Configuration", test_telegram_config),
        ("Device Connection", test_device_connection),
        ("Appium Server", test_appium_server),
        ("SmartBot API", test_smartbot_api),
        ("Web Dashboard", test_web_dashboard),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
    elif passed >= total - 2:
        print("⚠️ Most tests passed. System is mostly ready.")
    else:
        print("❌ Multiple tests failed. Please check configuration.")
    
    print("\n💡 Next steps:")
    if passed >= total - 2:
        print("1. Start SmartBot: python3 smartbot.py")
        print("2. Access dashboard: http://localhost:80")
        print("3. Monitor logs: tail -f smartbot.log")
    else:
        print("1. Fix failed tests")
        print("2. Run installation script: ./install.sh")
        print("3. Re-run this test")

if __name__ == "__main__":
    main() 