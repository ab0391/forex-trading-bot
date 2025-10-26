#!/bin/bash

# One-Line Enhanced Trading Bot Deployment
# This script creates and starts the enhanced trading bot with fresh API key

echo "🚀 Starting Enhanced Trading Bot Deployment..."

# Stop all existing fxbot services
echo "Stopping existing services..."
sudo systemctl stop fxbot-enhanced-watchdog.service 2>/dev/null || true
sudo systemctl stop fxbot-enhanced-watchdog.timer 2>/dev/null || true
sudo systemctl stop fxbot-run.service 2>/dev/null || true
sudo systemctl stop fxbot-run.timer 2>/dev/null || true
sudo systemctl stop fxbot-fixed-rate-limiter.service 2>/dev/null || true
sudo systemctl stop fxbot-fixed-rate-limiter.timer 2>/dev/null || true
sudo systemctl stop fxbot-net-watchdog.service 2>/dev/null || true
sudo systemctl stop fxbot-single-call.timer 2>/dev/null || true
sudo systemctl stop fxbot-single-call.service 2>/dev/null || true

# Wait for services to stop
sleep 3

# Create new enhanced service
echo "Creating enhanced service..."
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

# Create timer
echo "Creating timer..."
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

# Enable and start
echo "Enabling and starting new service..."
sudo systemctl daemon-reload
sudo systemctl enable fxbot-enhanced-fresh-api.timer
sudo systemctl start fxbot-enhanced-fresh-api.timer

# Show status
echo "✅ Deployment complete! Status:"
sudo systemctl status fxbot-enhanced-fresh-api.timer --no-pager -l

echo ""
echo "📊 Enhanced Trading Bot Features:"
echo "✅ Fresh API Key: d0b9148c9634439bba31a2b9fd753c2a"
echo "✅ 16-Symbol Rotation: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CHF, NZD/USD, USD/CAD, EUR/GBP, EUR/JPY, GBP/JPY, AUD/JPY, EUR/CHF, GBP/CHF, AUD/CAD, NZD/CAD, CAD/JPY"
echo "✅ Rate Limiter: 8.6 second intervals (≤7 calls/minute)"
echo "✅ Scan Schedule: Every 30 minutes"
echo ""
echo "🔍 Monitor with: journalctl -u fxbot-enhanced-fresh-api.service -f"
echo "📈 Expected: No more 9/1/9/1 pattern, clean credit usage"