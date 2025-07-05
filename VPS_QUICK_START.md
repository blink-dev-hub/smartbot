# 🚀 SmartBot VPS Quick Start

## 📋 **ESSENTIAL COMMANDS**

### **1. Upload Project**
```bash
# From your local machine
scp -r backend/ root@YOUR_VPS_IP:/opt/smartbot/
scp -r frontend/ root@YOUR_VPS_IP:/opt/smartbot/
```

### **2. VPS Setup**
```bash
# SSH to VPS
ssh root@YOUR_VPS_IP

# Install dependencies
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv adb curl wget git

# Install Node.js & Appium
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
npm install -g appium appium-uiautomator2-driver
```

### **3. Project Setup**
```bash
cd /opt/smartbot

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install

# Systemd service
cp smartbot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable smartbot.service
chmod +x smartbot.py
```

### **4. Connect Android Device**
```bash
# Connect device via USB
adb devices
# Should show: 8b9abf39    device

# Get device info
adb devices -l
```

### **5. Configure SmartBot**
```bash
nano config.json
# Update device_udid with your device ID
# Update telegram bot_token and chat_id
```

### **6. Start Services**
```bash
# Start Appium
appium &

# Start SmartBot
systemctl start smartbot

# Check status
systemctl status smartbot
```

### **7. Test System**
```bash
# Run comprehensive test
python3 test_system.py

# Check logs
tail -f smartbot.log
journalctl -u smartbot -f
```

### **8. Access Dashboard**
```bash
# Test locally
curl http://localhost:80

# Access from browser
http://YOUR_VPS_IP:80
# Login: vladislav / smartbot
```

---

## 🔧 **TROUBLESHOOTING**

### **Device Issues**
```bash
adb kill-server && adb start-server
adb devices
lsusb  # Check USB connection
```

### **Appium Issues**
```bash
pkill -f appium
appium &
curl http://localhost:4723/status
```

### **SmartBot Issues**
```bash
systemctl status smartbot
journalctl -u smartbot -f
cd /opt/smartbot && source venv/bin/activate && python3 smartbot.py
```

### **Playwright Issues**
```bash
playwright install
playwright --version
```

---

## 📊 **MONITORING**

### **Check System Health**
```bash
# Service status
systemctl status smartbot

# Live logs
tail -f smartbot.log

# System test
python3 test_system.py

# Database events
sqlite3 smartbot.db "SELECT COUNT(*) FROM events;"
```

### **Performance Monitoring**
```bash
# System resources
htop
df -h
free -h

# Network
netstat -tlnp | grep -E "(80|5000|4723)"
```

---

## 🎯 **SUCCESS CHECKLIST**

- [ ] `adb devices` shows your device
- [ ] `curl http://localhost:4723/status` returns ready
- [ ] `systemctl status smartbot` shows active
- [ ] `python3 test_system.py` passes all tests
- [ ] `http://YOUR_VPS_IP:80` loads dashboard
- [ ] `ls screenshots/` shows test images
- [ ] Telegram alerts are received
- [ ] `smartbot.log` shows OTT test results

---

## 🚀 **PRODUCTION COMMANDS**

### **Service Management**
```bash
# Start/Stop/Restart
systemctl start smartbot
systemctl stop smartbot
systemctl restart smartbot

# Enable/Disable
systemctl enable smartbot
systemctl disable smartbot

# View logs
journalctl -u smartbot -f
```

### **Manual Control**
```bash
cd /opt/smartbot
source venv/bin/activate
python3 smartbot.py  # Manual start
```

### **Backup**
```bash
# Create backup
tar -czf smartbot_backup_$(date +%Y%m%d).tar.gz /opt/smartbot/

# Restore backup
tar -xzf smartbot_backup_YYYYMMDD.tar.gz -C /
```

---

## 📞 **SUPPORT**

### **Logs Location**
- SmartBot: `/opt/smartbot/smartbot.log`
- System: `journalctl -u smartbot`
- Screenshots: `/opt/smartbot/screenshots/`
- Database: `/opt/smartbot/smartbot.db`

### **Configuration**
- Main config: `/opt/smartbot/config.json`
- Service file: `/etc/systemd/system/smartbot.service`

### **Test Commands**
```bash
# Quick health check
python3 test_system.py

# API test
curl http://localhost:5000/api/status

# Dashboard test
curl http://localhost:80
```

---

**🎉 Ready for Production!** 