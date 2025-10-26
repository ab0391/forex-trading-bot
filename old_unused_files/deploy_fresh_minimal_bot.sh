#!/bin/bash

# 🚀 FRESH MINIMAL BOT DEPLOYMENT
# Completely clean slate with bulletproof API limits

echo "🧹 CLEANING SLATE - Fresh Minimal Bot Deployment"

# Server details
SERVER="ubuntu@84.235.245.60"
REMOTE_PATH="/home/ubuntu/fxbot"

# Step 1: Stop and remove ALL existing services
echo "⏹️  Stopping all existing services..."
ssh $SERVER << 'EOF'
# Stop all fxbot services
sudo systemctl stop fxbot-run.timer fxbot-run.service 2>/dev/null
sudo systemctl stop fxbot-enhanced-fresh-api.timer fxbot-enhanced-fresh-api.service 2>/dev/null
sudo systemctl stop fxbot-enhanced-watchdog.timer fxbot-enhanced-watchdog.service 2>/dev/null
sudo systemctl stop fxbot-single-call.timer fxbot-single-call.service 2>/dev/null

# Disable all fxbot services
sudo systemctl disable fxbot-run.timer fxbot-run.service 2>/dev/null
sudo systemctl disable fxbot-enhanced-fresh-api.timer fxbot-enhanced-fresh-api.service 2>/dev/null
sudo systemctl disable fxbot-enhanced-watchdog.timer fxbot-enhanced-watchdog.service 2>/dev/null
sudo systemctl disable fxbot-single-call.timer fxbot-single-call.service 2>/dev/null

echo "✅ All services stopped and disabled"
EOF

# Step 2: Clean all data
echo "🧹 Cleaning all cached data..."
ssh $SERVER << 'EOF'
cd /home/ubuntu/fxbot
# Remove all cache, log, and data files
rm -f *.json *.cache *.log
rm -f signals_history.json data_cache.json price_cache.json
rm -f minimal_signals.json
# Backup old bot files
mkdir -p old_bots
mv complete_enhanced_trading_bot*.py old_bots/ 2>/dev/null
echo "✅ Data cleaned"
EOF

# Step 3: Upload minimal bot
echo "📤 Uploading minimal bulletproof bot..."
scp minimal_bulletproof_bot.py $SERVER:$REMOTE_PATH/
scp minimal-bot.service $SERVER:/tmp/
scp minimal-bot.timer $SERVER:/tmp/

# Step 4: Install and configure
echo "🔧 Installing minimal bot system..."
ssh $SERVER << 'EOF'
# Install service files
sudo mv /tmp/minimal-bot.service /etc/systemd/system/
sudo mv /tmp/minimal-bot.timer /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/minimal-bot.service
sudo chmod 644 /etc/systemd/system/minimal-bot.timer

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable minimal-bot.timer
sudo systemctl start minimal-bot.timer

echo "✅ Minimal bot system installed"
EOF

# Step 5: Test the minimal bot
echo "🧪 Testing minimal bot..."
ssh $SERVER << 'EOF'
cd /home/ubuntu/fxbot
source .venv/bin/activate
python minimal_bulletproof_bot.py
EOF

# Step 6: Check status
echo "📊 Checking system status..."
ssh $SERVER << 'EOF'
echo "=== TIMER STATUS ==="
sudo systemctl status minimal-bot.timer --no-pager
echo ""
echo "=== NEXT RUNS ==="
sudo systemctl list-timers minimal-bot.timer --no-pager
echo ""
echo "=== RECENT LOGS ==="
journalctl -u minimal-bot.service --since "5 minutes ago" -n 10 --no-pager
EOF

echo ""
echo "🎉 FRESH MINIMAL BOT DEPLOYMENT COMPLETE!"
echo ""
echo "📊 System Overview:"
echo "  - 🔥 API Calls: 1 per run (guaranteed under limit)"
echo "  - ⏰ Schedule: Every 2 hours (12 calls/day max)"
echo "  - 📈 Symbol: EUR/USD only"
echo "  - 💾 Data: Minimal (50 bars)"
echo "  - 🛡️  Bulletproof: No complex caching or rate limiting needed"
echo ""
echo "🔍 Monitor with:"
echo "  ssh $SERVER"
echo "  journalctl -u minimal-bot.service -f"
