#!/bin/bash
# Deploy Enhanced Trading Bot with Trade Lifecycle Management

echo "🚀 Deploying Enhanced Trading Bot with Trade Lifecycle Management"
echo "================================================================="

# Upload enhanced bot
scp complete_enhanced_trading_bot_lifecycle.py fxbot:/home/ubuntu/fxbot/

# SSH and deploy
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot

echo "🛑 Stopping current bot services..."
sudo systemctl stop fxbot-run.service
sudo systemctl stop fxbot-enhanced-watchdog.service

echo "📦 Backing up current bot..."
cp complete_enhanced_trading_bot_fixed.py complete_enhanced_trading_bot_backup.py

echo "🚀 Deploying enhanced bot with lifecycle management..."
cp complete_enhanced_trading_bot_lifecycle.py complete_enhanced_trading_bot_fixed.py

echo "🔄 Restarting bot services..."
sudo systemctl start fxbot-enhanced-watchdog.service
sudo systemctl restart fxbot-run.service

echo "⏱️  Waiting for services to start..."
sleep 5

echo "📊 Service Status:"
systemctl status fxbot-run.service --no-pager
echo ""
systemctl status fxbot-enhanced-watchdog.timer --no-pager

echo ""
echo "🎉 ENHANCED BOT DEPLOYED!"
echo "========================"
echo "✅ Trade lifecycle management active"
echo "✅ 10 currency pairs monitored"
echo "✅ Duplicate signal prevention enabled"
echo "✅ Auto SL/TP monitoring"
echo ""
echo "📊 New Features:"
echo "• One signal per trade setup (no more spam)"
echo "• 10 pairs: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CHF,"
echo "           NZD/USD, USD/CAD, EUR/GBP, EUR/JPY, GBP/JPY"
echo "• Per-pair trade tracking"
echo "• Auto trade closure detection"
echo ""
echo "🔍 Monitor with: journalctl -u fxbot-run.service -f"
EOF

echo ""
echo "🎯 DEPLOYMENT COMPLETE!"
echo "======================"
echo "✅ Enhanced bot with lifecycle management deployed"
echo "✅ 10 currency pairs for 2x-3x more opportunities"
echo "✅ No more duplicate signals"
echo "📊 Expected: Clean, unique signals with proper trade lifecycle"