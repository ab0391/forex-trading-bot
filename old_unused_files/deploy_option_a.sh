#!/bin/bash

# 🚀 OPTION A: OPTIMAL TRADING BOT DEPLOYMENT
# 6 pairs per hour, H4 strategy, 6 API calls/hour (75% under limit)

echo "🚀 Deploying OPTION A: Optimal Trading Bot"

# Server details
SERVER="ubuntu@84.235.245.60"
REMOTE_PATH="/home/ubuntu/fxbot"

# Step 1: Stop enhanced bot (causing 16/8 issue)
echo "⏹️  Stopping problematic enhanced bot..."
ssh $SERVER << 'EOF'
sudo systemctl stop enhanced-bot.timer enhanced-bot.service 2>/dev/null
sudo systemctl disable enhanced-bot.timer enhanced-bot.service 2>/dev/null
echo "✅ Enhanced bot stopped (was causing 16/8 credits)"
EOF

# Step 2: Upload Option A bot
echo "📤 Uploading Option A optimal bot..."
scp option_a_optimal_bot.py $SERVER:$REMOTE_PATH/
scp optimal-bot.service $SERVER:/tmp/
scp optimal-bot.timer $SERVER:/tmp/

# Step 3: Install and configure
echo "🔧 Installing Option A system..."
ssh $SERVER << 'EOF'
# Install service files
sudo mv /tmp/optimal-bot.service /etc/systemd/system/
sudo mv /tmp/optimal-bot.timer /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/optimal-bot.service
sudo chmod 644 /etc/systemd/system/optimal-bot.timer

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable optimal-bot.timer
sudo systemctl start optimal-bot.timer

echo "✅ Option A system installed"
EOF

# Step 4: Test Option A bot
echo "🧪 Testing Option A optimal bot..."
ssh $SERVER << 'EOF'
cd /home/ubuntu/fxbot
source .venv/bin/activate
python option_a_optimal_bot.py
EOF

# Step 5: Check status
echo "📊 Checking Option A system status..."
ssh $SERVER << 'EOF'
echo "=== TIMER STATUS ==="
sudo systemctl status optimal-bot.timer --no-pager
echo ""
echo "=== NEXT RUNS ==="
sudo systemctl list-timers optimal-bot.timer --no-pager
echo ""
echo "=== RECENT LOGS ==="
journalctl -u optimal-bot.service --since "5 minutes ago" -n 10 --no-pager
EOF

echo ""
echo "🎉 OPTION A: OPTIMAL TRADING BOT DEPLOYMENT COMPLETE!"
echo ""
echo "📊 System Overview:"
echo "  - 📈 Strategy: 6 pairs per hour (H4 enhanced analysis)"
echo "  - ⏰ Schedule: Every hour at :10 minutes"
echo "  - 🔥 API Calls: 6 per hour (75% under 8/min limit)"
echo "  - 📊 Coverage: All 12 pairs every 2 hours"
echo "  - 🎯 Signals: Enhanced H4 with MACD, RSI, zones"
echo "  - ✅ Problem Fixed: No more 16/8 credit issues"
echo ""
echo "🔍 Monitor with:"
echo "  ssh $SERVER"
echo "  journalctl -u optimal-bot.service -f"
