#!/bin/bash

# Deploy Trading Bot with Fixed Rate Limiter
# This script deploys the corrected bot that properly spaces API calls

echo "🚀 Deploying Trading Bot with Fixed Rate Limiter..."
echo "🎯 Goal: Eliminate 9/1/9/1 credit pattern and minutely violations"
echo "=" * 60

# Server details
SERVER_IP="144.126.254.179"
SERVER_USER="ubuntu"
BOT_DIR="/home/ubuntu/fxbot"

echo "📂 Step 1: Uploading corrected bot file..."

# Upload the corrected bot file
scp complete_enhanced_trading_bot_optimized.py ${SERVER_USER}@${SERVER_IP}:${BOT_DIR}/

# Upload the rate limiter file
scp rate_limiter.py ${SERVER_USER}@${SERVER_IP}:${BOT_DIR}/

echo "🛑 Step 2: Stopping current bot services..."

# SSH to server and deploy
ssh ${SERVER_USER}@${SERVER_IP} << 'REMOTE_COMMANDS'

# Stop all existing fxbot services
echo "Stopping all FX bot services..."
sudo systemctl stop fxbot-enhanced-watchdog.service 2>/dev/null || true
sudo systemctl stop fxbot-enhanced-watchdog.timer 2>/dev/null || true
sudo systemctl stop fxbot-run.service 2>/dev/null || true
sudo systemctl stop fxbot-run.timer 2>/dev/null || true

# Wait a moment for services to stop
sleep 3

echo "✅ All FX bot services stopped"

echo "📝 Step 3: Creating new service for fixed bot..."

# Create new service file for the fixed bot
sudo tee /etc/systemd/system/fxbot-fixed-rate-limiter.service > /dev/null << 'SERVICE_EOF'
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
SERVICE_EOF

# Create timer for 30-minute intervals
sudo tee /etc/systemd/system/fxbot-fixed-rate-limiter.timer > /dev/null << 'TIMER_EOF'
[Unit]
Description=Run FX Bot with Fixed Rate Limiter every 30 minutes
Requires=fxbot-fixed-rate-limiter.service

[Timer]
OnBootSec=3min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
TIMER_EOF

echo "🔄 Step 4: Reloading systemd and enabling new service..."

# Reload systemd and enable the new service
sudo systemctl daemon-reload
sudo systemctl enable fxbot-fixed-rate-limiter.timer
sudo systemctl start fxbot-fixed-rate-limiter.timer

echo "✅ Fixed rate limiter bot deployed successfully!"

# Check status
echo "📊 Service Status:"
sudo systemctl status fxbot-fixed-rate-limiter.timer --no-pager -l

echo ""
echo "📋 Monitoring Commands:"
echo "• Check timer status: sudo systemctl status fxbot-fixed-rate-limiter.timer"
echo "• View logs: journalctl -u fxbot-fixed-rate-limiter.service -f"
echo "• Manual run: sudo systemctl start fxbot-fixed-rate-limiter.service"

REMOTE_COMMANDS

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "📊 Expected Results:"
echo "• Rate limiter enforces 8.6 second intervals between API calls"
echo "• Each scan takes ~2-3 minutes instead of rapid succession"
echo "• TwelveData minutely maximum should stay ≤7/8 calls"
echo "• 9/1/9/1 credit pattern should be eliminated"
echo ""
echo "🔍 Next Steps:"
echo "1. Monitor TwelveData dashboard for credit patterns"
echo "2. Check logs: ssh ${SERVER_USER}@${SERVER_IP} 'journalctl -u fxbot-fixed-rate-limiter.service -f'"
echo "3. Verify minutely maximum stays under 8 calls"
echo ""
echo "⚠️  If issues persist, check the ultra-minimal bot option in CREDIT_PATTERN_ANALYSIS.md"