# SmartBot OTT Automation System

A comprehensive automation system for OTT streaming services with IP rotation, geo-block bypass, and real-time monitoring.

## 🚀 Features

- **Multi-Platform OTT Testing**: Hotstar (Android), SonyLIV & Zee5 (Browser)
- **Real-time Web Dashboard**: Live monitoring and control
- **IP Rotation System**: Automatic SIM switching and IP management
- **Geo-block Detection**: Smart detection and bypass of regional restrictions
- **Telegram Integration**: Real-time alerts and notifications
- **Screenshot Capture**: Visual evidence of all tests
- **DRM Detection**: Advanced DRM handshake monitoring
- **Production Ready**: Systemd service, auto-restart, logging

## 📋 System Requirements

- **OS**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.8+
- **Node.js**: 18+
- **Android Device**: USB debugging enabled
- **RAM**: 2GB+
- **Storage**: 10GB+

## 🛠️ Installation

### Quick Install
```bash
# Clone the repository
git clone <repository-url>
cd smartbot/backend

# Make install script executable
chmod +x install.sh

# Run installation
./install.sh
```

### Manual Install
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv adb curl wget

# Install Node.js and Appium
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g appium appium-uiautomator2-driver

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install

# Set up systemd service
sudo cp smartbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartbot.service
```

## 🔧 Configuration

### 1. Device Setup
```bash
# Connect Android device
adb devices

# Verify device is connected
adb -s <device-id> shell echo "connected"
```

### 2. Update config.json
```json
{
  "paths": {
    "log": "smartbot.log",
    "screenshots": "screenshots",
    "ipcache": "ip_cache.json",
    "database": "smartbot.db"
  },
  "ott_services": {
    "hotstar": {
      "mode": "android",
      "appPackage": "in.startv.hotstar",
      "appActivity": "com.hotstar.MainActivity",
      "device_udid": "<your-device-id>",
      "appium_server_url": "http://localhost:4723",
      "url": "https://www.hotstar.com/in"
    },
    "sonyliv": {
      "mode": "browser",
      "url": "https://www.sonyliv.com"
    },
    "zee5": {
      "mode": "browser",
      "url": "https://www.zee5.com"
    }
  },
  "telegram": {
    "bot_token": "<your-bot-token>",
    "chat_id": "<your-chat-id>"
  },
  "api": {
    "host": "0.0.0.0",
    "port": 5000
  }
}
```

### 3. Telegram Setup (Optional)
1. Create a bot with @BotFather
2. Get your chat ID
3. Update config.json with bot_token and chat_id

## 🚀 Usage

### Start the Service
```bash
# Start SmartBot
sudo systemctl start smartbot

# Check status
sudo systemctl status smartbot

# View logs
sudo journalctl -u smartbot -f
```

### Manual Start (Development)
```bash
cd smartbot/backend
source venv/bin/activate
python3 smartbot.py
```

### Web Dashboard
- **URL**: http://localhost:80
- **Login**: vladislav / smartbot
- **Features**: Real-time monitoring, logs, screenshots, control

### API Endpoints
- **Status**: GET http://localhost:5000/api/status
- **Logs**: GET http://localhost:5000/api/logs
- **Screenshots**: GET http://localhost:5000/api/screenshots
- **Control**: POST http://localhost:5000/api/control/{pause|resume|rotate}

## 📊 Monitoring

### Dashboard Features
- ✅ Real-time OTT test results
- ✅ Live log streaming
- ✅ Screenshot gallery
- ✅ DRM handshake events
- ✅ IP rotation history
- ✅ System status monitoring

### Telegram Alerts
- ✅ OTT test success/failure
- ✅ DRM handshake detection
- ✅ System status changes
- ✅ Error notifications

## 🔍 Troubleshooting

### Common Issues

#### 1. Device Not Connected
```bash
# Check device connection
adb devices

# Restart ADB server
adb kill-server
adb start-server
```

#### 2. Appium Server Issues
```bash
# Start Appium server
appium

# Check if port 4723 is available
netstat -tlnp | grep 4723
```

#### 3. Playwright Issues
```bash
# Reinstall Playwright browsers
playwright install

# Check browser installation
playwright --version
```

#### 4. Service Won't Start
```bash
# Check service logs
sudo journalctl -u smartbot -f

# Check file permissions
ls -la smartbot.py
chmod +x smartbot.py
```

### Log Files
- **Main Log**: `smartbot.log`
- **System Logs**: `sudo journalctl -u smartbot`
- **Screenshots**: `screenshots/` directory

## 🏗️ Architecture

### Components
1. **SmartBot Core** (`smartbot.py`): Main automation engine
2. **OTT Checker** (`ott_checker.py`): OTT service testing
3. **Device Manager** (`device_manager.py`): IP/SIM management
4. **Web API** (`api.py`): REST API and Socket.IO
5. **Frontend** (`frontend/`): Web dashboard
6. **Database** (`database.py`): Event logging

### Data Flow
```
Android Device → SmartBot → OTT Testing → Results → Dashboard/Telegram
     ↓              ↓           ↓           ↓
   IP Rotation → Logging → Screenshots → Alerts
```

## 🔒 Security

- **Authentication**: Web dashboard login required
- **API Security**: Local network only
- **Data Privacy**: All data stored locally
- **Device Security**: USB debugging only when needed

## 📈 Performance

- **Test Frequency**: Configurable (default: 5 minutes)
- **Response Time**: <30 seconds per OTT service
- **Resource Usage**: Low CPU/memory footprint
- **Scalability**: Supports multiple devices

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files
3. Check system status
4. Contact support with logs and screenshots

## 📄 License

This project is proprietary software. All rights reserved.

---

**SmartBot OTT Automation System** - Production Ready ✅ 