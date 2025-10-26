# 🚀 Manual Deployment Instructions - Fixed Rate Limiter Bot

## 🚨 **URGENT: Server Connection Issue**

The automated deployment failed due to server connection timeout. Please follow these manual steps to deploy the fixed rate limiter bot.

---

## 📋 **Manual Deployment Steps**

### **Step 1: Connect to Oracle Server**
```bash
# Try connecting to the server directly
ssh ubuntu@144.126.254.179

# If connection fails, check:
# 1. Server is running
# 2. SSH key is properly configured
# 3. Network connectivity
```

### **Step 2: Upload Fixed Files**
Once connected, upload these corrected files:

```bash
# Upload from local machine
scp complete_enhanced_trading_bot_optimized.py ubuntu@144.126.254.179:/home/ubuntu/fxbot/
scp rate_limiter.py ubuntu@144.126.254.179:/home/ubuntu/fxbot/
```

### **Step 3: Stop Current Services**
```bash
# SSH to server
ssh ubuntu@144.126.254.179

# Stop all existing FX bot services
sudo systemctl stop fxbot-enhanced-watchdog.service
sudo systemctl stop fxbot-enhanced-watchdog.timer
sudo systemctl stop fxbot-run.service
sudo systemctl stop fxbot-run.timer

# Verify no services are running
sudo systemctl list-units | grep fxbot
```

### **Step 4: Create New Service**
```bash
# Create service file for fixed bot
sudo tee /etc/systemd/system/fxbot-fixed-rate-limiter.service > /dev/null << 'EOF'
[Unit]
Description=FX Trading Bot with Fixed Rate Limiter
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
sudo tee /etc/systemd/system/fxbot-fixed-rate-limiter.timer > /dev/null << 'EOF'
[Unit]
Description=Run FX Bot with Fixed Rate Limiter every 30 minutes
Requires=fxbot-fixed-rate-limiter.service

[Timer]
OnBootSec=3min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

### **Step 6: Enable and Start Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start the timer
sudo systemctl enable fxbot-fixed-rate-limiter.timer
sudo systemctl start fxbot-fixed-rate-limiter.timer

# Check status
sudo systemctl status fxbot-fixed-rate-limiter.timer
```

---

## ✅ **Verification Steps**

### **1. Check Service Status**
```bash
sudo systemctl status fxbot-fixed-rate-limiter.timer
sudo systemctl status fxbot-fixed-rate-limiter.service
```

### **2. Monitor Logs**
```bash
# Watch real-time logs
journalctl -u fxbot-fixed-rate-limiter.service -f

# Check for rate limiter messages
journalctl -u fxbot-fixed-rate-limiter.service | grep "wait_for_api_call"
```

### **3. Manual Test Run**
```bash
# Run the bot manually to test
sudo systemctl start fxbot-fixed-rate-limiter.service

# Check logs for proper timing
journalctl -u fxbot-fixed-rate-limiter.service --since "1 minute ago"
```

---

## 🎯 **Expected Results After Deployment**

### **Rate Limiter Behavior:**
- ✅ **8.6 second intervals** between each API call
- ✅ **2-3 minute total scan time** (instead of rapid succession)
- ✅ **Maximum 7 calls per minute** (well under 8 limit)

### **TwelveData Dashboard:**
- ✅ **Consistent credit usage** instead of 9/1/9/1 pattern
- ✅ **Minutely maximum ≤7/8** calls (no more violations)
- ✅ **Smooth credit consumption** over time

### **Log Messages to Look For:**
```
🛡️ Rate limiter: Waiting 8.6 seconds before API call...
📞 API Call: TwelveData request after rate limit delay
✅ Scan completed with proper API spacing
```

---

## 🚨 **Troubleshooting**

### **If Rate Limits Still Occur:**
1. **Check logs** for rate limiter activation messages
2. **Verify only one service** is running (no conflicts)
3. **Consider ultra-minimal bot** (see CREDIT_PATTERN_ANALYSIS.md)

### **If Connection Still Fails:**
1. **Server may be down** - check server status
2. **Try different SSH key** or connection method
3. **Contact server administrator**

### **Emergency Fallback:**
If issues persist, deploy the ultra-minimal bot instead:
```bash
# Use the ultra-minimal bot (1 API call per scan)
python3 ultra_minimal_trading_bot.py
```

---

## 📊 **Files Modified in This Fix**

### **complete_enhanced_trading_bot_optimized.py**
- **Lines 483-484**: Added rate limiter before HTTP request in `fetch_time_series_data()`
- **Lines 543-544**: Added rate limiter before HTTP request in `get_current_price()`
- **Removed redundant calls** from lines 413 and 519

### **rate_limiter.py**
- **Unchanged** - already properly implemented with 8.6 second intervals

---

**Created**: 2025-09-29 (Current)
**Status**: Ready for manual deployment
**Priority**: HIGH - Deploy immediately to fix 9/1/9/1 pattern