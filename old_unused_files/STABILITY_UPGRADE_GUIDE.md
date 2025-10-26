# ZoneSync FX Bot - Stability Upgrade Guide

## Overview
This upgrade fixes critical stability issues that were causing your Oracle server to require reboots every couple of days. The enhanced bot will now run autonomously without manual intervention.

## What Was Fixed

### 1. **Main Loop Crash Protection** ✅
- **Problem**: Any unhandled exception would crash the entire bot
- **Solution**: Comprehensive error handling with exponential backoff
- **File**: `multi_strategy_trading_tool_fixed.py`

### 2. **API Connection Resilience** ✅
- **Problem**: No retry logic, connection pooling, or timeout handling
- **Solution**: HTTP session with connection pooling and automatic retries
- **File**: `multi_strategy_trading_tool_fixed.py` (RobustDataFetcher class)

### 3. **SMTP Email Blocking** ✅
- **Problem**: Email operations could hang indefinitely
- **Solution**: Timeouts, retry logic, and fallback notifications
- **File**: `robust_notifier.py`

### 4. **Missing Function Bug** ✅
- **Problem**: `_send_retest_email` function missing, causing NameError crashes
- **Solution**: Complete function implementation with proper error handling
- **File**: `zones_block_fixed.py`

### 5. **Enhanced System Monitoring** ✅
- **Problem**: Basic network watchdog insufficient for complex failures
- **Solution**: Comprehensive health monitoring with intelligent recovery
- **File**: `enhanced_network_watchdog.py`

## Installation Instructions

### Step 1: Backup Current System
```bash
# On your Oracle server
cd /home/ubuntu/fxbot
cp -r . ../fxbot_backup_$(date +%Y%m%d)
```

### Step 2: Upload New Files
Upload these files to your Oracle server `/home/ubuntu/fxbot/` directory:

1. `multi_strategy_trading_tool_fixed.py`
2. `robust_notifier.py`
3. `zones_block_fixed.py`
4. `enhanced_network_watchdog.py`

### Step 3: Install Required Dependencies
```bash
sudo pip3 install psutil requests urllib3
```

### Step 4: Update Your Main Script
```bash
# Backup original
cp multi_strategy_trading_tool.py multi_strategy_trading_tool_original.py

# Replace with fixed version
cp multi_strategy_trading_tool_fixed.py multi_strategy_trading_tool.py
```

### Step 5: Update Systemd Services

#### Create Enhanced Watchdog Service
```bash
sudo nano /etc/systemd/system/fxbot-enhanced-watchdog.service
```

Add this content:
```ini
[Unit]
Description=ZoneSync Enhanced Network Watchdog
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
Environment=PYTHONPATH=/home/ubuntu/fxbot
ExecStart=/home/ubuntu/fxbot/.venv/bin/python3 enhanced_network_watchdog.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Create Enhanced Watchdog Timer
```bash
sudo nano /etc/systemd/system/fxbot-enhanced-watchdog.timer
```

Add this content:
```ini
[Unit]
Description=Run ZoneSync Enhanced Watchdog every 5 minutes
Requires=fxbot-enhanced-watchdog.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

### Step 6: Enable and Start Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Disable old watchdog (if exists)
sudo systemctl stop fxbot-net-watchdog.timer
sudo systemctl disable fxbot-net-watchdog.timer

# Enable new enhanced watchdog
sudo systemctl enable fxbot-enhanced-watchdog.timer
sudo systemctl start fxbot-enhanced-watchdog.timer

# Restart main bot service
sudo systemctl restart fxbot-run.timer
sudo systemctl restart fxbot-run.service

# Check status
sudo systemctl status fxbot-run.timer fxbot-enhanced-watchdog.timer
```

### Step 7: Verify Installation
```bash
# Check all services are running
systemctl list-timers --no-pager | grep fxbot

# Check logs
journalctl -u fxbot-run.service -f
journalctl -u fxbot-enhanced-watchdog.service -f

# Generate health report
cd /home/ubuntu/fxbot
/home/ubuntu/fxbot/.venv/bin/python3 enhanced_network_watchdog.py --report
```

## Environment Variables Update

Add these new optional variables to your `.env` file:

```bash
# Email configuration (if not already set)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=alerts@yourdomain.com
EMAIL_PASSWORD=your-app-password

# Telegram backup notifications (optional but recommended)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# System monitoring thresholds (optional)
CPU_THRESHOLD=90
MEMORY_THRESHOLD=90
DISK_THRESHOLD=90
```

## New Features

### 1. **Intelligent Error Recovery**
- Progressive backoff on failures (5min → 10min → 15min → 20min → 25min)
- Extended sleep (6 hours) after repeated failures
- Automatic reset of failure counters on success

### 2. **Connection Pool Management**
- Reuses HTTP connections for better performance
- Automatic retry with exponential backoff
- Handles rate limiting intelligently

### 3. **Dual Notification System**
- Email with SMTP timeouts and retries
- Telegram as backup notification method
- Automatic fallback if one method fails

### 4. **Comprehensive Health Monitoring**
- CPU, memory, and disk usage monitoring
- Network connectivity testing
- Service and process health checks
- DNS resolution verification
- Automatic recovery actions

### 5. **Graceful Shutdown**
- Responds to SIGTERM and SIGINT signals
- Clean exit without hanging processes
- Proper resource cleanup

## Monitoring Commands

### Check System Health
```bash
# Real-time health report
/home/ubuntu/fxbot/.venv/bin/python3 enhanced_network_watchdog.py --report

# Check service status
systemctl status fxbot-run.service fxbot-enhanced-watchdog.service

# View recent logs
journalctl -u fxbot-run.service -n 50
journalctl -u fxbot-enhanced-watchdog.service -n 50
```

### Manual Testing
```bash
# Test notifications
cd /home/ubuntu/fxbot
/home/ubuntu/fxbot/.venv/bin/python3 -c "from robust_notifier import notifier; print(notifier.test_notifications())"

# Test zone management
/home/ubuntu/fxbot/.venv/bin/python3 zones_block_fixed.py

# Manual bot run (with new stability features)
/home/ubuntu/fxbot/.venv/bin/python3 multi_strategy_trading_tool_fixed.py
```

## Expected Improvements

After this upgrade, you should see:

1. **No More Server Reboots Required** - Bot handles all failures gracefully
2. **Better API Reliability** - Connection pooling and retries prevent hanging
3. **Faster Issue Detection** - Enhanced monitoring catches problems early
4. **Automatic Recovery** - System self-heals from common failure modes
5. **Better Visibility** - Comprehensive logging and health reports
6. **Dual Notifications** - Never miss critical alerts

## Troubleshooting

### If the Bot Still Hangs
1. Check logs: `journalctl -u fxbot-run.service -f`
2. Check health: `/home/ubuntu/fxbot/.venv/bin/python3 enhanced_network_watchdog.py --report`
3. Restart services: `sudo systemctl restart fxbot-run.service`

### If You Don't Receive Notifications
1. Test notifications: `python3 robust_notifier.py`
2. Check environment variables in `.env`
3. Verify email/Telegram credentials

### If Watchdog Doesn't Recover Issues
1. Check watchdog logs: `journalctl -u fxbot-enhanced-watchdog.service -f`
2. Manually trigger recovery: `sudo systemctl restart fxbot-run.service`
3. Check network connectivity: `ping api.twelvedata.com`

## Rollback Plan

If you need to rollback to the original system:

```bash
cd /home/ubuntu/fxbot

# Stop new services
sudo systemctl stop fxbot-enhanced-watchdog.timer
sudo systemctl disable fxbot-enhanced-watchdog.timer

# Restore original files
cp multi_strategy_trading_tool_original.py multi_strategy_trading_tool.py

# Restart original services
sudo systemctl restart fxbot-run.service
sudo systemctl start fxbot-net-watchdog.timer  # if it existed
```

## Support

The enhanced bot logs extensively. If you encounter issues:

1. Check `/home/ubuntu/fxbot/bot.log`
2. Check `/home/ubuntu/fxbot/watchdog.log`
3. Run health report for system status
4. Check systemd service logs

Your bot should now run autonomously without requiring manual Oracle server reboots!