#!/bin/bash

# 🚀 Smart Rotation Trading Bot Deployment Script
# This uploads and deploys the enhanced bot with 10-symbol rotation

echo "🚀 Starting deployment of Smart Rotation Trading Bot..."

# Server details
SERVER="ubuntu@84.235.245.60"
REMOTE_PATH="/home/ubuntu/fxbot"

# Step 1: Test connection
echo "📡 Testing server connection..."
if ssh -o ConnectTimeout=10 $SERVER "echo 'Connection successful'"; then
    echo "✅ Server connection OK"
else
    echo "❌ Server connection failed!"
    echo "Please check:"
    echo "  - Server is running"
    echo "  - SSH key is configured"
    echo "  - Network connectivity"
    exit 1
fi

# Step 2: Upload files
echo "📤 Uploading enhanced bot files..."
scp complete_enhanced_trading_bot_optimized.py $SERVER:$REMOTE_PATH/
scp rate_limiter.py $SERVER:$REMOTE_PATH/
scp .env $SERVER:$REMOTE_PATH/

# Step 3: Deploy on server
echo "🔧 Deploying on server..."
ssh $SERVER << 'EOF'
cd /home/ubuntu/fxbot

# Backup current version
echo "💾 Creating backup..."
cp complete_enhanced_trading_bot_fixed.py complete_enhanced_trading_bot_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null || echo "No existing bot to backup"

# Stop existing services
echo "⏹️  Stopping existing services..."
sudo systemctl stop fxbot-enhanced-watchdog.service 2>/dev/null
sudo systemctl stop fxbot-enhanced-watchdog.timer 2>/dev/null
sudo systemctl stop fxbot-run.service 2>/dev/null
sudo systemctl stop fxbot-run.timer 2>/dev/null

# Deploy new version
echo "🚀 Deploying smart rotation bot..."
cp complete_enhanced_trading_bot_optimized.py complete_enhanced_trading_bot_fixed.py

# Restart service
echo "▶️  Starting enhanced service..."
sudo systemctl start fxbot-run.service
sudo systemctl enable fxbot-run.service

# Check status
echo "📊 Service status:"
sudo systemctl status fxbot-run.service --no-pager -l

echo "✅ Deployment complete!"
echo "📈 Bot now scanning 10 major pairs with smart rotation"
echo "🎯 Expected: 8 API calls per cycle, all pairs covered every 5 cycles"
EOF

echo ""
echo "🎉 Smart Rotation Trading Bot Deployment Complete!"
echo ""
echo "📊 What happens next:"
echo "  - Bot scans 2 pairs per cycle (8 API calls)"
echo "  - Rotates through all 10 major pairs"
echo "  - Full coverage every 5 cycles (~2.5 hours)"
echo "  - TwelveData usage should drop to ~2 credits per cycle"
echo ""
echo "🔍 Monitor with:"
echo "  ssh $SERVER"
echo "  journalctl -u fxbot-run.service -f"
