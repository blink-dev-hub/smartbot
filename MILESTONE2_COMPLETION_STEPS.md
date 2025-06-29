# Milestone 2 Completion Steps

## **🎯 What You Need to Do RIGHT NOW:**

### **Step 1: Prepare Your Code for VPS (15 minutes)**

```bash
# 1. Create a deployment package
cd smartbot
zip -r smartbot_deployment.zip . -x "venv/*" "*.pyc" "__pycache__/*"

# 2. Or use git (if you have a repository)
git init
git add .
git commit -m "Milestone 2 ready for deployment"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### **Step 2: Deploy to Client's VPS (1 hour)**

**A. Get VPS Access from Client:**
- Ask for SSH credentials
- Get VPS IP address
- Confirm Ubuntu 22.04 LTS

**B. Deploy SmartBot:**
```bash
# Connect to VPS
ssh root@CLIENT_VPS_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv git wireguard

# Enable IP forwarding
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Create SmartBot directory
cd /opt
sudo mkdir smartbot
sudo chown $USER:$USER smartbot
cd smartbot

# Upload your code (choose one method)
# Method 1: SCP
scp -r /path/to/your/smartbot/* root@CLIENT_VPS_IP:/opt/smartbot/

# Method 2: Git
git clone YOUR_REPO_URL .

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
playwright install
```

### **Step 3: Configure SmartBot (30 minutes)**

```bash
cd backend

# Create config file
cp config.json.example config.json

# Edit configuration
nano config.json
```

**Add this to config.json:**
```json
{
  "ott_services": {
    "hotstar": "https://www.hotstar.com",
    "sonyliv": "https://www.sonyliv.com",
    "zee5": "https://www.zee5.com"
  },
  "vpn_config": {
    "interface": "wg0",
    "subnet": "10.8.0.0/24"
  },
  "telegram": {
    "bot_token": "ASK_CLIENT_FOR_BOT_TOKEN",
    "chat_id": "ASK_CLIENT_FOR_CHAT_ID"
  },
  "check_interval": 300,
  "screenshot_dir": "screenshots",
  "vps_mode": true
}
```

### **Step 4: Setup WireGuard VPN (30 minutes)**

```bash
# Generate server keys
wg genkey | sudo tee /etc/wireguard/private.key
sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key

# Create server config
sudo nano /etc/wireguard/wg0.conf
```

**Server Config:**
```ini
[Interface]
PrivateKey = YOUR_SERVER_PRIVATE_KEY
Address = 10.8.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```

```bash
# Start WireGuard
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```

### **Step 5: Test SmartBot Backend (15 minutes)**

```bash
cd /opt/smartbot/backend

# Test mode
python3 smartbot.py --test

# Check if it's working
tail -f smartbot.log
```

### **Step 6: Test Frontend Dashboard (15 minutes)**

```bash
cd /opt/smartbot/frontend

# Install Flask
pip install flask requests

# Run dashboard
python3 app.py

# Test access
curl http://localhost:5001
```

### **Step 7: Connect SIM Devices (1 hour)**

**For each SIM device, create WireGuard config:**

```ini
[Interface]
PrivateKey = CLIENT_PRIVATE_KEY
Address = 10.8.0.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = SERVER_PUBLIC_KEY
Endpoint = CLIENT_VPS_IP:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

**Add client to server:**
```bash
sudo wg set wg0 peer CLIENT_PUBLIC_KEY allowed-ips 10.8.0.2/32
```

### **Step 8: Test DRM Workflow (1 hour)**

```bash
# Test OTT services
curl -I https://www.hotstar.com
curl -I https://www.sonyliv.com
curl -I https://www.zee5.com

# Test SmartBot OTT checks
cd /opt/smartbot/backend
python3 smartbot.py --test

# Check screenshots
ls -la screenshots/
```

### **Step 9: Test Multi-User (30 minutes)**

```bash
# Test multiple concurrent connections
# Verify auto SIM rotation
# Test failover scenarios
```

### **Step 10: Run Validation Tests (30 minutes)**

```bash
cd /opt/smartbot
python3 milestone2_testing.py

# Check test results
cat milestone2_test_report.json
```

## **📋 Milestone 2 Validation Checklist:**

### **Infrastructure** ✅
- [ ] VPS deployed and accessible
- [ ] SmartBot running on VPS
- [ ] WireGuard tunnels established
- [ ] SIM devices connected

### **Health Checks** ✅
- [ ] Ping functionality working
- [ ] OTT site access verified
- [ ] Flag detection system ready
- [ ] Health monitoring active

### **WireGuard Tunnels** ✅
- [ ] Dynamic tunnel creation/removal
- [ ] Multiple SIM support
- [ ] Auto failover working
- [ ] Routing table manipulation

### **DRM Workflow** ✅
- [ ] Widevine authentication
- [ ] PlayReady authentication
- [ ] Per-user license distribution
- [ ] OTT authentication working

### **Multi-User** ✅
- [ ] Concurrent user support
- [ ] Auto SIM rotation
- [ ] Load handling
- [ ] Performance acceptable

### **Alerts** ✅
- [ ] Telegram alerts working
- [ ] Tunnel failure notifications
- [ ] SIM issue alerts
- [ ] OTT block detection

### **Documentation** ✅
- [ ] All scripts documented
- [ ] Flows documented
- [ ] Setup guides complete
- [ ] Testing procedures documented

## **📊 Deliverables for Client:**

### **Files to Send:**
1. **Screenshots** of working system
2. **Test logs** showing successful operations
3. **Performance metrics**
4. **Configuration files** (with sensitive data redacted)
5. **Documentation** of all flows

### **Proof of Work:**
- VPS deployment screenshots
- SmartBot running logs
- OTT test results
- Dashboard screenshots
- Telegram alert examples

## **🎯 Milestone 2 Completion Status:**

**After completing these steps:**
- ✅ **SmartBot deployed** on VPS
- ✅ **SIM devices connected** and working
- ✅ **DRM workflow tested** and validated
- ✅ **Multi-user testing** completed
- ✅ **All features working** in production
- ✅ **Documentation complete**

**Milestone 2 = COMPLETE** ✅

---

## **⏰ Timeline:**

- **Steps 1-6**: 2 hours (deployment and basic setup)
- **Steps 7-8**: 2 hours (SIM integration and DRM testing)
- **Steps 9-10**: 1 hour (multi-user testing and validation)
- **Documentation**: 30 minutes

**Total: 5.5 hours to complete Milestone 2**

---

**Ready to start? Begin with Step 1 and work through each step systematically!** 