#!/bin/bash
# Reset Dashboard for Enhanced Bot with $10 Trade Template

echo "🔄 Resetting Dashboard for Enhanced Bot Integration"
echo "================================================="

# SSH into server and reset
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot

echo "🛑 Stopping dashboard service..."
sudo systemctl stop fxbot-dashboard.service

echo "📦 Backing up old signals..."
if [ -f signals_history.json ]; then
    cp signals_history.json signals_history_backup_$(date +%Y%m%d_%H%M%S).json
    echo "✅ Backup created"
fi

echo "🧹 Clearing old signals data..."
echo "[]" > signals_history.json

echo "🧹 Clearing active trades (if exists)..."
if [ -f active_trades.json ]; then
    cp active_trades.json active_trades_backup_$(date +%Y%m%d_%H%M%S).json
    echo "{}" > active_trades.json
else
    echo "{}" > active_trades.json
fi

echo "🚀 Starting fresh dashboard service..."
sudo systemctl start fxbot-dashboard.service

echo "⏱️  Waiting for service to start..."
sleep 3

echo "📊 Dashboard service status:"
systemctl status fxbot-dashboard.service --no-pager

echo ""
echo "✅ DASHBOARD RESET COMPLETE!"
echo "============================"
echo "📊 Clean signals_history.json created"
echo "🔄 Active trades cleared"
echo "📈 Ready for enhanced bot integration"
echo "💰 $10 trade template ready"
echo ""
echo "🎯 Next: Deploy enhanced bot to start fresh tracking"
EOF

echo ""
echo "🎉 DASHBOARD RESET SUCCESSFUL!"
echo "=============================="
echo "✅ Old duplicate signals cleared"
echo "✅ Fresh start for enhanced bot"
echo "✅ $10 trade template ready"
echo "📊 Dashboard accessible via SSH tunnel: http://localhost:8080"