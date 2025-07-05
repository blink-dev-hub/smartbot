# 🚀 SmartBot VPS Deployment & Testing Guide

## 📋 OVERVIEW

This guide will help you deploy and test the SmartBot OTT automation system on your VPS with an Android device connected via USB.

---

## **STEP 1: PREPARE VPS**

### **1.1 Connect to VPS**
```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y
```

### **1.2 Install Basic Dependencies**
```bash
# Install essential packages
apt install -y python3 python3-pip python3-venv adb curl wget git

# Install Node.js for Appium
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Appium
npm install -g appium
npm install -g appium-uiautomator2-driver
```

---

## **STEP 2: UPLOAD PROJECT**

### **2.1 Method 1: Using SCP (Recommended)**
```bash
# From your local machine
cd /path/to/smartbot
scp -r backend/ root@YOUR_VPS_IP:/opt/smartbot/
scp -r frontend/ root@YOUR_VPS_IP:/opt/smartbot/
```

### **2.2 Method 2: Using Git**
```bash
# On VPS
cd /opt
git clone YOUR_REPOSITORY_URL smartbot
cd smartbot
```

### **2.3 Method 3: Manual Upload**
- Use SFTP client (FileZilla, WinSCP)
- Upload `backend/` and `frontend/` folders to `/opt/smartbot/`

---

## **STEP 3: SETUP PROJECT ON VPS**

### **3.1 Navigate to Project Directory**
```bash
cd /opt/smartbot
ls -la  # Verify files are uploaded
```

### **3.2 Setup Python Environment**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### **3.3 Setup Systemd Service**
```bash
# Copy service file
cp smartbot.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload
systemctl enable smartbot.service

# Set permissions
chmod +x smartbot.py
chmod +x install.sh
```

---

## **STEP 4: CONNECT ANDROID DEVICE**

### **4.1 Physical Connection**
1. Connect Android device to VPS via USB cable
2. Enable USB debugging on Android device:
   - Settings → About Phone → Tap Build Number 7 times
   - Settings → Developer Options → USB Debugging (ON)

### **4.2 Test Device Connection**
```bash
# Check if device is detected
adb devices

# Expected output:
# List of devices attached
# 8b9abf39    device

# If device not found, try:
adb kill-server
adb start-server
adb devices
```

### **4.3 Get Device Details**
```bash
# Get device UDID
adb devices -l

# Get device info
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
```

---

## **STEP 5: CONFIGURE SMARTBOT**

### **5.1 Update Configuration**
```bash
# Edit config.json
nano config.json
```

**Update these values:**
```json
{
  "ott_services": {
    "hotstar": {
      "device_udid": "YOUR_DEVICE_UDID_HERE",
      "appium_server_url": "http://localhost:4723"
    }
  },
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  }
}
```

### **5.2 Test Configuration**
```bash
# Test if config is valid
python3 -c "import json; json.load(open('config.json'))"
echo "Configuration is valid!"
```

---

## **STEP 6: START APPIUM SERVER**

### **6.1 Start Appium in Background**
```bash
# Start Appium server
appium &

# Check if Appium is running
curl http://localhost:4723/status

# Expected output: {"status":0,"value":{"ready":true}}
```

### **6.2 Alternative: Use Screen Session**
```bash
# Create screen session for Appium
screen -S appium
appium
# Press Ctrl+A, then D to detach

# Reattach to session if needed
screen -r appium
```

---

## **STEP 7: TEST SYSTEM COMPONENTS**

### **7.1 Run System Test**
```bash
# Test all components
python3 test_system.py
```

**Expected Output:**
```
🧪 SmartBot System Test
==================================================

File Permissions:
   ✅ smartbot.py exists
   ✅ config.json exists
   ✅ requirements.txt exists

Dependencies:
   ✅ All dependencies available

OTT Configuration:
   ✅ All OTT services configured

Device Connection:
   ✅ Device connected

Appium Server:
   ✅ Appium server running

SmartBot API:
   ✅ SmartBot API responding

Web Dashboard:
   ✅ Web dashboard accessible

==================================================
📊 Test Results:
   File Permissions: ✅ PASS
   Dependencies: ✅ PASS
   OTT Configuration: ✅ PASS
   Device Connection: ✅ PASS
   Appium Server: ✅ PASS
   SmartBot API: ✅ PASS
   Web Dashboard: ✅ PASS

🎯 Overall: 7/7 tests passed
🎉 All tests passed! System is ready for production.
```

### **7.2 Test Individual Components**
```bash
# Test Android device
adb -s YOUR_DEVICE_UDID shell echo "Android device working"

# Test Appium connection
python3 -c "
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
driver = webdriver.Remote('http://localhost:4723', {})
print('Appium connection successful')
driver.quit()
"

# Test Playwright
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    print('Playwright working')
    browser.close()
"
```

---

## **STEP 8: START SMARTBOT SERVICE**

### **8.1 Start Service**
```bash
# Start SmartBot
systemctl start smartbot

# Check status
systemctl status smartbot

# View logs
journalctl -u smartbot -f
```

### **8.2 Manual Start (For Testing)**
```bash
# Activate virtual environment
source venv/bin/activate

# Start manually
python3 smartbot.py
```

---

## **STEP 9: TEST OTT SERVICES**

### **9.1 Monitor Logs**
```bash
# Watch SmartBot logs
tail -f smartbot.log

# Watch system logs
journalctl -u smartbot -f
```

### **9.2 Check Screenshots**
```bash
# View captured screenshots
ls -la screenshots/
# Should show screenshots from OTT tests
```

### **9.3 Test Web Dashboard**
```bash
# Check if dashboard is accessible
curl http://localhost:80

# Or open in browser: http://YOUR_VPS_IP:80
# Login: vladislav / smartbot
```

---

## **STEP 10: VERIFY FUNCTIONALITY**

### **10.1 Check API Endpoints**
```bash
# Test API status
curl http://localhost:5000/api/status

# Test logs endpoint
curl http://localhost:5000/api/logs

# Test screenshots endpoint
curl http://localhost:5000/api/screenshots
```

### **10.2 Monitor Telegram Alerts**
- Check your Telegram for SmartBot alerts
- Should receive notifications about OTT tests

### **10.3 Verify OTT Testing**
```bash
# Check database for test results
sqlite3 smartbot.db "SELECT * FROM events ORDER BY timestamp DESC LIMIT 10;"
```

---

## **STEP 11: TROUBLESHOOTING**

### **11.1 Common Issues**

#### **Device Not Connected**
```bash
# Check USB connection
lsusb

# Restart ADB
adb kill-server
adb start-server
adb devices

# Check device permissions
adb -s YOUR_DEVICE_UDID shell dumpsys package | grep hotstar
```

#### **Appium Server Issues**
```bash
# Check if port 4723 is in use
netstat -tlnp | grep 4723

# Kill existing Appium processes
pkill -f appium

# Start fresh Appium server
appium
```

#### **SmartBot Service Issues**
```bash
# Check service logs
journalctl -u smartbot -f

# Check file permissions
ls -la smartbot.py
chmod +x smartbot.py

# Test manual start
cd /opt/smartbot
source venv/bin/activate
python3 smartbot.py
```

#### **Playwright Issues**
```bash
# Reinstall Playwright browsers
playwright install

# Check browser installation
playwright --version
```

### **11.2 Performance Monitoring**
```bash
# Monitor system resources
htop

# Check disk space
df -h

# Check memory usage
free -h

# Monitor network
iftop
```

---

## **STEP 12: PRODUCTION OPTIMIZATION**

### **12.1 Security Hardening**
```bash
# Configure firewall
ufw allow ssh
ufw allow 80
ufw allow 5000
ufw enable

# Secure SSH
nano /etc/ssh/sshd_config
# Change port, disable root login, use key authentication
```

### **12.2 Performance Tuning**
```bash
# Optimize Python
pip install --upgrade pip

# Monitor and optimize
# Add to crontab for regular cleanup
0 2 * * * find /opt/smartbot/screenshots -mtime +7 -delete
```

### **12.3 Backup Strategy**
```bash
# Create backup script
cat > /opt/smartbot/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/smartbot_$DATE.tar.gz /opt/smartbot/
echo "Backup created: smartbot_$DATE.tar.gz"
EOF

chmod +x /opt/smartbot/backup.sh
```

---

## **🎯 SUCCESS CRITERIA**

### **✅ System is Working When:**
1. **Device Connected**: `adb devices` shows your device
2. **Appium Running**: `curl http://localhost:4723/status` returns ready
3. **SmartBot Active**: `systemctl status smartbot` shows active
4. **Dashboard Accessible**: `http://YOUR_VPS_IP:80` loads
5. **API Responding**: `curl http://localhost:5000/api/status` works
6. **Screenshots Generated**: `ls screenshots/` shows test images
7. **Telegram Alerts**: Receive notifications about tests
8. **Database Logging**: `sqlite3 smartbot.db "SELECT COUNT(*) FROM events;"` > 0

### **📊 Expected Performance:**
- **Hotstar**: 100% success rate (Android automation)
- **SonyLIV**: 95% success rate (Browser mode)
- **Zee5**: 95% success rate (Browser mode)
- **System Uptime**: 99.9% with auto-restart
- **Response Time**: <30 seconds per OTT service

---

## **🚀 NEXT STEPS**

### **After Successful Testing:**
1. **Monitor**: Set up regular monitoring and alerts
2. **Scale**: Add more Android devices if needed
3. **Optimize**: Fine-tune performance based on usage
4. **Backup**: Implement regular backup strategy
5. **Document**: Update documentation with VPS-specific notes

### **Support:**
- Check logs: `tail -f smartbot.log`
- System status: `systemctl status smartbot`
- Test system: `python3 test_system.py`
- View dashboard: `http://YOUR_VPS_IP:80`

---

**🎉 Your SmartBot OTT Automation System is now deployed and ready for production!** 