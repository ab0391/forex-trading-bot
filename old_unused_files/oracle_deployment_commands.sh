#!/bin/bash
# Oracle Server Deployment Commands for Rate Limit Fix
# Run these commands on your Oracle server to deploy the fix

echo "🚀 Deploying Rate Limit Fix to Oracle Server"
echo "=============================================="

# Navigate to bot directory
cd /home/ubuntu/fxbot

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "📦 Creating backup..."
cp complete_enhanced_trading_bot_fixed.py "complete_enhanced_trading_bot_backup_${TIMESTAMP}.py"
echo "✅ Backup created: complete_enhanced_trading_bot_backup_${TIMESTAMP}.py"

# Copy rate-limited version to main bot file
echo "🔄 Deploying rate-limited bot..."
cp complete_enhanced_trading_bot_optimized.py complete_enhanced_trading_bot_fixed.py
echo "✅ Rate-limited bot deployed"

# Restart the service
echo "🔄 Restarting fxbot service..."
sudo systemctl restart fxbot-run.service

# Check service status
echo "📊 Checking service status..."
sudo systemctl status fxbot-run.service --no-pager

echo ""
echo "🎉 DEPLOYMENT COMPLETED!"
echo "========================"
echo ""
echo "📋 Monitoring Commands:"
echo "1. Watch logs in real-time:"
echo "   journalctl -u fxbot-run.service -f"
echo ""
echo "2. Watch rate limiter messages:"
echo "   journalctl -u fxbot-run.service -f | grep -E '(🛡️|🟢|⏳|⏱️|Rate limit)'"
echo ""
echo "3. Check for optimization messages:"
echo "   journalctl -u fxbot-run.service | grep -E '(Rate limiter|API call allowed|Enforcing minimum)'"
echo ""
echo "🎯 Expected Results:"
echo "- TwelveData dashboard: Minutely maximum ≤7/8 (GREEN)"
echo "- No red spikes above limit line in usage graph"
echo "- Log messages showing rate limiting in action"
echo ""
echo "📱 Next Check: Look at TwelveData dashboard in 10-15 minutes"
echo "   Should see smooth, consistent usage under the red limit line"
