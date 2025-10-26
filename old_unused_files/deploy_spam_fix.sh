#!/bin/bash
# Quick deployment script to fix Telegram spam issue

set -e

echo "🔧 Deploying Telegram Spam Fix..."
echo "=================================="

# Stop the service
echo "🛑 Stopping service..."
sudo systemctl stop fxbot-run.service

# Backup current version
echo "📦 Creating backup..."
cp multi_strategy_trading_tool.py multi_strategy_trading_tool_before_spam_fix.py

# Deploy fixed version
echo "🚀 Deploying spam-free version..."
cp complete_enhanced_trading_bot_fixed.py multi_strategy_trading_tool.py

# Test the fixed version
echo "🧪 Testing fixed version..."
.venv/bin/python3 -c "
from multi_strategy_trading_tool import TelegramNotifier
n = TelegramNotifier()
print('✅ Fixed version imports successfully')
result = n.send_message('🧪 Test: Spam fix deployed successfully!')
print(f'✅ Test message sent: {result}')
"

# Restart service
echo "🚀 Restarting service..."
sudo systemctl start fxbot-run.service

# Show status
echo "📊 Service status:"
systemctl status fxbot-run.service --no-pager -l

echo ""
echo "🎉 SPAM FIX DEPLOYED SUCCESSFULLY!"
echo "=================================="
echo "✅ Telegram spam prevention active"
echo "✅ Maximum 1 signal per symbol per scan"
echo "✅ Duplicate signal detection (1-hour cooldown)"
echo "✅ Zone deduplication (minimum 1 ATR apart)"
echo ""
echo "Your enhanced bot now sends clean, single alerts only!"