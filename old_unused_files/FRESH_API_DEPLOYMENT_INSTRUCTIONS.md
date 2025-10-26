# 🚀 Fresh API Key + Enhanced Rotation Deployment Instructions

## 🆕 **FRESH START: New TwelveData API Key Implementation**

**New API Key**: `d0b9148c9634439bba31a2b9fd753c2a`
- ✅ **Daily Credits**: 800 (fresh allocation)
- ✅ **Minutely Maximum**: 8 calls/minute
- ✅ **API Key Tested**: Working perfectly (EUR/USD = 1.17261)

---

## 🎯 **COMBINED DEPLOYMENT: Fresh API + Enhanced Features**

This deployment combines:
1. **Fresh TwelveData API key** (clean slate)
2. **16-symbol rotation system** (comprehensive coverage)
3. **Fixed rate limiter** (eliminates 9/1/9/1 pattern)

---

## 📋 **Manual Deployment Steps**

### **Step 1: Connect to Oracle Server**
```bash
# Connect to the server
ssh ubuntu@144.126.254.179

# If connection fails, check server status and SSH configuration
```

### **Step 2: Upload All Enhanced Files**
```bash
# Upload enhanced bot with 16-symbol rotation
scp complete_enhanced_trading_bot_optimized.py ubuntu@144.126.254.179:/home/ubuntu/fxbot/

# Upload rate limiter
scp rate_limiter.py ubuntu@144.126.254.179:/home/ubuntu/fxbot/

# Upload .env file with fresh API key
scp .env ubuntu@144.126.254.179:/home/ubuntu/fxbot/
```

### **Step 3: Stop All Current Services**
```bash
# SSH to server and stop everything
ssh ubuntu@144.126.254.179

# Stop all existing fxbot services
sudo systemctl stop fxbot-enhanced-watchdog.service
sudo systemctl stop fxbot-enhanced-watchdog.timer
sudo systemctl stop fxbot-run.service
sudo systemctl stop fxbot-run.timer
sudo systemctl stop fxbot-fixed-rate-limiter.service
sudo systemctl stop fxbot-fixed-rate-limiter.timer

# Wait for full stop
sleep 5

# Verify nothing is running
sudo systemctl list-units | grep fxbot
```

### **Step 4: Create New Service with Fresh API**
```bash
# Create service file for enhanced bot with fresh API
sudo tee /etc/systemd/system/fxbot-enhanced-fresh-api.service > /dev/null << 'EOF'
[Unit]
Description=FX Trading Bot Enhanced (16-Symbol Rotation + Fresh API Key)
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
ExecStart=/usr/bin/python3 /home/ubuntu/fxbot/complete_enhanced_trading_bot_optimized.py
Environment=PATH=/usr/bin:/bin
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### **Step 5: Create Timer**
```bash
# Create timer for 30-minute intervals
sudo tee /etc/systemd/system/fxbot-enhanced-fresh-api.timer > /dev/null << 'EOF'
[Unit]
Description=Run Enhanced FX Bot with Fresh API Key every 30 minutes
Requires=fxbot-enhanced-fresh-api.service

[Timer]
OnBootSec=3min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

### **Step 6: Enable and Start**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start the timer
sudo systemctl enable fxbot-enhanced-fresh-api.timer
sudo systemctl start fxbot-enhanced-fresh-api.timer

# Check status
sudo systemctl status fxbot-enhanced-fresh-api.timer
```

---

## ✅ **Verification Steps**

### **1. Check Service Status**
```bash
sudo systemctl status fxbot-enhanced-fresh-api.timer
sudo systemctl status fxbot-enhanced-fresh-api.service
```

### **2. Monitor Fresh API Key Usage**
```bash
# Watch for enhanced rotation logs
journalctl -u fxbot-enhanced-fresh-api.service -f

# Check for fresh API key usage
journalctl -u fxbot-enhanced-fresh-api.service | grep "Enhanced Rotation"

# Look for rate limiter enforcement
journalctl -u fxbot-enhanced-fresh-api.service | grep "Enforcing minimum interval"
```

### **3. Manual Test Run**
```bash
# Test the enhanced bot manually
sudo systemctl start fxbot-enhanced-fresh-api.service

# Check logs immediately
journalctl -u fxbot-enhanced-fresh-api.service --since "1 minute ago"
```

---

## 🎯 **Expected Results with Fresh API Key**

### **Enhanced Symbol Rotation:**
- ✅ **16 major currency pairs** scanned via rotation
- ✅ **2 symbols per scan** = 8 API calls total
- ✅ **Complete coverage** every 8 scans (4 hours)

### **Fresh API Key Benefits:**
- ✅ **Clean credit tracking** starting from 0
- ✅ **No historical rate limit violations**
- ✅ **Fresh 800 credit allocation**
- ✅ **Clean TwelveData account state**

### **Rate Limiter Performance:**
- ✅ **8.6 second intervals** between API calls
- ✅ **Maximum 7 calls per minute** (under 8 limit)
- ✅ **No more 9/1/9/1 pattern**
- ✅ **Consistent credit usage**

---

## 📊 **Log Messages to Look For**

### **Enhanced Rotation Logs:**
```
🎯 Enhanced Rotation - Scan 1
📊 Current Cycle: 1/8 | Symbols: ['EUR/USD', 'GBP/USD']
🔄 Full Rotations Completed: 0
📈 Coverage: 16 major pairs | API calls: 2 × 4 timeframes = 8
```

### **Rate Limiter Logs:**
```
🛡️ Rate limiter: Waiting 8.6 seconds before API call...
📞 API Call: TwelveData request after rate limit delay
🟢 API call allowed. Recent calls: 3/7
⏱️ Enforcing minimum interval. Waiting 8.6s...
```

### **Completion Logs:**
```
✅ ENHANCED SCAN CYCLE COMPLETE
📊 Current cycle results: 2 signals sent | API calls: 8
🎯 Next scan cycle 2: 2/8 | Symbols: ['USD/JPY', 'AUD/USD']
```

---

## 🚨 **Troubleshooting**

### **If Fresh API Key Still Shows Issues:**
1. **Problem is definitively in our code** (not API key related)
2. **Check rate limiter enforcement** in logs
3. **Verify only one service running**
4. **Consider ultra-minimal bot** as emergency fallback

### **If Connection Still Fails:**
1. **Check server status** with hosting provider
2. **Verify SSH key configuration**
3. **Try different network/VPN**

---

## 📈 **Expected TwelveData Dashboard Results**

### **With Fresh API Key:**
- **Clean usage starting from 0/800**
- **Consistent credit consumption** (no 9/1/9/1 pattern)
- **Minutely maximum ≤7/8** calls
- **Predictable usage**: ~1 credit every 8.6 seconds during scans

### **Rotation Pattern:**
- **Scan 1**: EUR/USD, GBP/USD (8 credits)
- **Scan 2**: USD/JPY, AUD/USD (8 credits)
- **Scan 3**: USD/CHF, NZD/USD (8 credits)
- **...and so on through all 16 pairs**

---

## 🔑 **Key Files with Fresh API Key**

### **Updated .env File:**
```bash
TWELVEDATA_API_KEY=d0b9148c9634439bba31a2b9fd753c2a
TELEGRAM_BOT_TOKEN=your_telegram_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### **Enhanced Bot Features:**
- ✅ 16-symbol rotation system
- ✅ Fixed rate limiter (8.6s intervals)
- ✅ Fresh API key integration
- ✅ Comprehensive logging and statistics

---

**Status**: Ready for manual deployment
**Priority**: HIGH - Fresh API key + enhanced features
**Expected Outcome**: Complete elimination of 9/1/9/1 pattern with comprehensive market coverage

This deployment gives us the best possible chance of success by combining a fresh API key with all our enhancements.