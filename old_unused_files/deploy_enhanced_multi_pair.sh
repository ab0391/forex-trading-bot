#!/bin/bash

# 🚀 ENHANCED MULTI-PAIR BOT DEPLOYMENT
# 12 major pairs, hourly scans, zone detection strategy

echo "🚀 Deploying Enhanced Multi-Pair Trading Bot"

# Server details
SERVER="ubuntu@84.235.245.60"
REMOTE_PATH="/home/ubuntu/fxbot"

# Step 1: Stop minimal bot
echo "⏹️  Stopping minimal bot..."
ssh $SERVER << 'EOF'
sudo systemctl stop minimal-bot.timer minimal-bot.service 2>/dev/null
sudo systemctl disable minimal-bot.timer minimal-bot.service 2>/dev/null
echo "✅ Minimal bot stopped"
EOF

# Step 2: Upload enhanced bot
echo "📤 Uploading enhanced multi-pair bot..."
scp enhanced_multi_pair_bot.py $SERVER:$REMOTE_PATH/
scp enhanced-bot.service $SERVER:/tmp/
scp enhanced-bot.timer $SERVER:/tmp/

# Step 3: Install and configure
echo "🔧 Installing enhanced bot system..."
ssh $SERVER << 'EOF'
# Install service files
sudo mv /tmp/enhanced-bot.service /etc/systemd/system/
sudo mv /tmp/enhanced-bot.timer /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/enhanced-bot.service
sudo chmod 644 /etc/systemd/system/enhanced-bot.timer

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable enhanced-bot.timer
sudo systemctl start enhanced-bot.timer

echo "✅ Enhanced bot system installed"
EOF

# Step 4: Test the enhanced bot
echo "🧪 Testing enhanced multi-pair bot..."
ssh $SERVER << 'EOF'
cd /home/ubuntu/fxbot
source .venv/bin/activate
python enhanced_multi_pair_bot.py
EOF

# Step 5: Check status
echo "📊 Checking system status..."
ssh $SERVER << 'EOF'
echo "=== TIMER STATUS ==="
sudo systemctl status enhanced-bot.timer --no-pager
echo ""
echo "=== NEXT RUNS ==="
sudo systemctl list-timers enhanced-bot.timer --no-pager
echo ""
echo "=== RECENT LOGS ==="
journalctl -u enhanced-bot.service --since "5 minutes ago" -n 15 --no-pager
EOF

echo ""
echo "🎉 ENHANCED MULTI-PAIR BOT DEPLOYMENT COMPLETE!"
echo ""
echo "📊 System Overview:"
echo "  - 📈 Pairs: 12 major + popular crosses"
echo "  - 🔄 Rotation: 4 pairs per hour"
echo "  - ⏰ Schedule: Every hour at :05 minutes"
echo "  - 🔥 API Calls: 12 per hour (288/day vs 800 limit)"
echo "  - 🎯 Strategy: Multi-timeframe zone detection"
echo "  - 📊 Coverage: All pairs scanned every 3 hours"
echo ""
echo "🔍 Monitor with:"
echo "  ssh $SERVER"
echo "  journalctl -u enhanced-bot.service -f"
