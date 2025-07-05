#!/bin/bash

echo "🚀 SmartBot Installation Script"
echo "================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run as root. Use a regular user."
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv adb curl wget

# Install Android SDK (if not already installed)
if ! command -v adb &> /dev/null; then
    echo "📱 Installing Android SDK..."
    wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip
    unzip platform-tools-latest-linux.zip
    sudo mv platform-tools /opt/
    echo 'export PATH=$PATH:/opt/platform-tools' >> ~/.bashrc
    source ~/.bashrc
    rm platform-tools-latest-linux.zip
fi

# Install Node.js and Appium
echo "📱 Installing Node.js and Appium..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Appium
echo "📱 Installing Appium..."
npm install -g appium
npm install -g appium-uiautomator2-driver

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

# Set up systemd service
echo "🔧 Setting up systemd service..."
sudo cp smartbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartbot.service

echo "✅ Installation complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Connect your Android device via USB"
echo "2. Enable USB debugging on the device"
echo "3. Run: adb devices (to verify connection)"
echo "4. Start the service: sudo systemctl start smartbot"
echo "5. Check status: sudo systemctl status smartbot"
echo "6. View logs: sudo journalctl -u smartbot -f"
echo ""
echo "🌐 Web Dashboard: http://localhost:80"
echo "📱 API Endpoint: http://localhost:5000" 