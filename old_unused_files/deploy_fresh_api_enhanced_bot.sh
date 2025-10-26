#!/bin/bash

# Deploy Enhanced Trading Bot with Fresh TwelveData API Key
# Combines: 16-symbol rotation + rate limiter fix + fresh API key

echo "🚀 Deploying Enhanced Trading Bot with Fresh API Key"
echo "🎯 Features: 16-symbol rotation + rate limiter + fresh API allocation"
echo "=" * 70

# Server details
SERVER_IP="84.235.245.60"
SERVER_USER="ubuntu"
BOT_DIR="/home/ubuntu/fxbot"

echo "📊 Fresh API Key Details:"
echo "   • TwelveData Key: d0b9148c9634439bba31a2b9fd753c2a"
echo "   • Daily Credits: 800 (fresh allocation)"
echo "   • Minutely Max: 8 calls/minute"
echo "   • Strategy: 16 pairs rotated, 2 per scan = 8 API calls"
echo ""

echo "📂 Step 1: Uploading enhanced bot files with fresh API key..."

# Upload the enhanced bot file with 16-symbol rotation
scp complete_enhanced_trading_bot_optimized.py ${SERVER_USER}@${SERVER_IP}:${BOT_DIR}/

# Upload the rate limiter file
scp rate_limiter.py ${SERVER_USER}@${SERVER_IP}:${BOT_DIR}/

# Upload the updated .env file with fresh API key
scp .env ${SERVER_USER}@${SERVER_IP}:${BOT_DIR}/

echo "🛑 Step 2: Stopping current bot services and deploying fresh system..."

# SSH to server and deploy
ssh ${SERVER_USER}@${SERVER_IP} << 'REMOTE_COMMANDS'

# Stop all existing fxbot services
echo "Stopping all existing FX bot services..."
sudo systemctl stop fxbot-enhanced-watchdog.service 2>/dev/null || true
sudo systemctl stop fxbot-enhanced-watchdog.timer 2>/dev/null || true
sudo systemctl stop fxbot-run.service 2>/dev/null || true
sudo systemctl stop fxbot-run.timer 2>/dev/null || true
sudo systemctl stop fxbot-fixed-rate-limiter.service 2>/dev/null || true
sudo systemctl stop fxbot-fixed-rate-limiter.timer 2>/dev/null || true

# Wait for services to fully stop
sleep 5

echo "✅ All previous FX bot services stopped"

echo "📝 Step 3: Creating new service for enhanced bot with fresh API key..."

# Create new service file for the enhanced bot
sudo tee /etc/systemd/system/fxbot-enhanced-fresh-api.service > /dev/null << 'SERVICE_EOF'
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
SERVICE_EOF

# Create timer for 30-minute intervals
sudo tee /etc/systemd/system/fxbot-enhanced-fresh-api.timer > /dev/null << 'TIMER_EOF'
[Unit]
Description=Run Enhanced FX Bot with Fresh API Key every 30 minutes
Requires=fxbot-enhanced-fresh-api.service

[Timer]
OnBootSec=3min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
TIMER_EOF

echo "🔄 Step 4: Enabling and starting enhanced bot with fresh API key..."

# Reload systemd and enable the new service
sudo systemctl daemon-reload
sudo systemctl enable fxbot-enhanced-fresh-api.timer
sudo systemctl start fxbot-enhanced-fresh-api.timer

echo "✅ Enhanced bot with fresh API key deployed successfully!"

# Check status
echo "📊 Service Status:"
sudo systemctl status fxbot-enhanced-fresh-api.timer --no-pager -l

echo ""
echo "📋 Monitoring Commands:"
echo "• Check timer status: sudo systemctl status fxbot-enhanced-fresh-api.timer"
echo "• View logs: journalctl -u fxbot-enhanced-fresh-api.service -f"
echo "• Manual run: sudo systemctl start fxbot-enhanced-fresh-api.service"
echo "• Check rotation: journalctl -u fxbot-enhanced-fresh-api.service | grep 'Enhanced Rotation'"

REMOTE_COMMANDS

echo ""
echo "🎉 ENHANCED DEPLOYMENT COMPLETE!"
echo ""
echo "📊 System Overview:"
echo "✅ Fresh TwelveData API Key: d0b9148c9634439bba31a2b9fd753c2a"
echo "✅ Enhanced Symbol Rotation: 16 major currency pairs"
echo "✅ Smart Rotation Strategy: 2 symbols per scan = 8 API calls"
echo "✅ Rate Limiter: 8.6 second intervals between calls"
echo "✅ Complete Coverage: All 16 pairs every 8 scans (4 hours)"
echo ""
echo "🔍 Expected Results:"
echo "• Clean credit usage starting from 0 with fresh key"
echo "• No more 9/1/9/1 pattern - should see consistent usage"
echo "• Minutely maximum stays ≤7/8 calls"
echo "• All 16 major pairs covered via rotation"
echo "• Rotation logs: 'Enhanced Rotation - Scan X' messages"
echo ""
echo "🔍 Next Steps:"
echo "1. Monitor TwelveData dashboard for clean credit patterns"
echo "2. Check logs: ssh ${SERVER_USER}@${SERVER_IP} 'journalctl -u fxbot-enhanced-fresh-api.service -f'"
echo "3. Verify rotation is working: Look for 'Current Cycle: X/8' messages"
echo "4. Confirm rate limiter: Look for 'Enforcing minimum interval' messages"
echo ""
echo "🆘 If issues persist after fresh API key, the problem is definitely in our code logic"