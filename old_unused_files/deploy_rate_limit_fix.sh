#!/bin/bash
# Quick Rate Limit Fix for ZoneSync Trading Bot
# Uses H1 close price instead of separate API call to avoid rate limits

echo "🔧 Deploying Rate Limit Fix..."

# Upload the fixed file
scp multi_strategy_trading_tool.py fxbot:/home/ubuntu/fxbot/

# Restart the service
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot
sudo systemctl restart fxbot-run.service
echo "✅ Bot restarted with rate limit fix"
echo "📊 Checking service status..."
sudo systemctl status fxbot-run.service --no-pager -l
EOF

echo ""
echo "🎯 Rate Limit Fix Applied!"
echo "• Now uses H1 close price instead of separate API call"
echo "• Reduces API usage by ~50%"
echo "• Should eliminate rate limit warnings"
echo ""
echo "Monitor with: ssh fxbot 'journalctl -u fxbot-run.service -f'"