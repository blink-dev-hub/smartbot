#!/bin/bash

echo "🚀 SmartBot VPS Deployment Script"
echo "=================================="

# Check if project files exist
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Project folders not found. Run this from the smartbot root directory."
    exit 1
fi

# Get VPS details
echo "📝 Enter VPS details:"
read -p "VPS IP address: " VPS_IP
read -p "VPS username (default: root): " VPS_USER
VPS_USER=${VPS_USER:-root}
read -p "SSH key path (optional): " SSH_KEY

# Create deployment package
echo "📦 Creating deployment package..."
DEPLOY_DIR="smartbot_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# Copy project files
cp -r backend $DEPLOY_DIR/
cp -r frontend $DEPLOY_DIR/
cp PROJECT_COMPLETE.md $DEPLOY_DIR/

# Create VPS setup script
cat > $DEPLOY_DIR/setup_vps.sh << 'EOF'
#!/bin/bash

echo "🚀 Setting up SmartBot on VPS..."
echo "================================="

# Update system
echo "📦 Updating system..."
apt update && apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt install -y python3 python3-pip python3-venv adb curl wget git

# Install Node.js
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Appium
echo "📱 Installing Appium..."
npm install -g appium
npm install -g appium-uiautomator2-driver

# Set up project directory
echo "📁 Setting up project directory..."
mkdir -p /opt/smartbot
cd /opt/smartbot

# Copy project files
cp -r backend/* .
cp -r frontend/* .

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
cp smartbot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable smartbot.service

# Set permissions
chown -R root:root /opt/smartbot
chmod +x /opt/smartbot/smartbot.py
chmod +x /opt/smartbot/install.sh

echo "✅ VPS setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Connect Android device via USB"
echo "2. Update config.json with device details"
echo "3. Start SmartBot service"
echo "4. Test the system"
EOF

chmod +x $DEPLOY_DIR/setup_vps.sh

# Create tar.gz package
tar -czf ${DEPLOY_DIR}.tar.gz $DEPLOY_DIR

echo "📦 Deployment package created: ${DEPLOY_DIR}.tar.gz"

# Upload to VPS
echo "📤 Uploading to VPS..."
if [ -n "$SSH_KEY" ]; then
    scp -i "$SSH_KEY" ${DEPLOY_DIR}.tar.gz ${VPS_USER}@${VPS_IP}:/tmp/
else
    scp ${DEPLOY_DIR}.tar.gz ${VPS_USER}@${VPS_IP}:/tmp/
fi

if [ $? -eq 0 ]; then
    echo "✅ Upload successful!"
    echo ""
    echo "🔗 Connect to VPS and run:"
    echo "ssh ${VPS_USER}@${VPS_IP}"
    echo ""
    echo "📦 Extract and setup:"
    echo "cd /tmp"
    echo "tar -xzf ${DEPLOY_DIR}.tar.gz"
    echo "cd ${DEPLOY_DIR}"
    echo "chmod +x setup_vps.sh"
    echo "./setup_vps.sh"
else
    echo "❌ Upload failed. Please check your SSH connection."
fi

# Cleanup
rm -rf $DEPLOY_DIR
rm ${DEPLOY_DIR}.tar.gz

echo ""
echo "🎯 Manual upload alternative:"
echo "1. Use SCP: scp -r smartbot/ ${VPS_USER}@${VPS_IP}:/opt/"
echo "2. Use SFTP client (FileZilla, WinSCP)"
echo "3. Use Git: git clone <your-repo> on VPS" 