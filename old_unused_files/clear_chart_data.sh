#!/bin/bash
# Clear All Dashboard Chart Data
# Ensures win rate trend and all graphs show clean slate

echo "📈 Clearing All Dashboard Chart Data"
echo "===================================="

# SSH into server and clear any remaining chart data
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot

echo "🔍 Looking for chart data files..."

# Find and clear any potential chart data files
find . -name "*chart*" -type f 2>/dev/null && echo "Found chart files"
find . -name "*trend*" -type f 2>/dev/null && echo "Found trend files"
find . -name "*analytics*" -type f 2>/dev/null && echo "Found analytics files"

# Clear any cached data files
if [ -f "chart_data.json" ]; then
    echo "🗑️ Clearing chart_data.json"
    echo "{}" > chart_data.json
fi

if [ -f "trend_data.json" ]; then
    echo "🗑️ Clearing trend_data.json"
    echo "[]" > trend_data.json
fi

if [ -f "analytics_cache.json" ]; then
    echo "🗑️ Clearing analytics_cache.json"
    echo "{}" > analytics_cache.json
fi

# Double-check main files are truly empty
echo "🧪 Verifying data files are empty..."
echo "signals_history.json content:"
cat signals_history.json

echo ""
echo "📊 Checking dashboard API responses..."

# Test API endpoints
echo "Stats API:"
curl -s localhost:8502/api/stats | jq '.' 2>/dev/null || curl -s localhost:8502/api/stats

echo ""
echo "Signals API:"
curl -s localhost:8502/api/signals | jq '.' 2>/dev/null || curl -s localhost:8502/api/signals

# Restart dashboard to clear any memory cache
echo ""
echo "🔄 Restarting dashboard to clear memory cache..."
sudo systemctl restart fxbot-dashboard.service
sleep 3

if systemctl is-active --quiet fxbot-dashboard.service; then
    echo "✅ Dashboard restarted successfully"
else
    echo "❌ Dashboard restart failed"
fi

echo ""
echo "✅ Chart data clearing completed"
EOF

echo ""
echo "🧹 CHART DATA CLEARED!"
echo "====================="
echo "📊 Dashboard restarted to clear memory cache"
echo "📈 All chart data should now show clean slate"
echo ""
echo "🔄 Clear your browser cache too:"
echo "• Chrome/Edge: Ctrl+Shift+Delete"
echo "• Firefox: Ctrl+Shift+Delete"
echo "• Safari: Cmd+Option+E"
echo ""
echo "🎯 Then refresh: http://localhost:8502"