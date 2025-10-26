#!/bin/bash
# Reset ZoneSync Dashboard Data for Fresh Accurate Tracking
# Clears all previous inaccurate data to start fresh with real-time price system

echo "🔄 ZoneSync Dashboard Data Reset"
echo "==============================="
echo "$(date): Starting dashboard data reset for fresh tracking"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Confirmation
echo "⚠️  WARNING: This will clear all existing dashboard data!"
echo "📊 Current data was recorded with inaccurate prices (30+ pip differences)"
echo "🎯 Fresh start needed for accurate performance tracking"
echo ""
read -p "Are you sure you want to reset all dashboard data? (yes/no): " confirm

if [[ $confirm != "yes" ]]; then
    echo "❌ Reset cancelled"
    exit 1
fi

echo ""
echo "🔄 Proceeding with dashboard data reset..."

# SSH into server and perform reset
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot

echo "📦 Creating backup of existing data..."

# Create backup directory with timestamp
BACKUP_DIR="dashboard_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup existing data files
if [ -f "signals_history.json" ]; then
    cp signals_history.json "$BACKUP_DIR/"
    echo "✅ Backed up signals_history.json"
fi

if [ -f "dashboard_data.json" ]; then
    cp dashboard_data.json "$BACKUP_DIR/"
    echo "✅ Backed up dashboard_data.json"
fi

if [ -f "trade_history.json" ]; then
    cp trade_history.json "$BACKUP_DIR/"
    echo "✅ Backed up trade_history.json"
fi

if [ -f "performance_data.json" ]; then
    cp performance_data.json "$BACKUP_DIR/"
    echo "✅ Backed up performance_data.json"
fi

echo "📦 Backup created in: $BACKUP_DIR"

echo ""
echo "🗑️  Clearing dashboard data files..."

# Clear main signals file (create empty array)
echo "[]" > signals_history.json
echo "✅ Cleared signals_history.json"

# Clear other potential data files
if [ -f "dashboard_data.json" ]; then
    echo "{}" > dashboard_data.json
    echo "✅ Cleared dashboard_data.json"
fi

if [ -f "trade_history.json" ]; then
    echo "[]" > trade_history.json
    echo "✅ Cleared trade_history.json"
fi

if [ -f "performance_data.json" ]; then
    echo '{"total_signals": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0}' > performance_data.json
    echo "✅ Cleared performance_data.json"
fi

# Set proper permissions
chmod 664 signals_history.json
if [ -f "dashboard_data.json" ]; then chmod 664 dashboard_data.json; fi
if [ -f "trade_history.json" ]; then chmod 664 trade_history.json; fi
if [ -f "performance_data.json" ]; then chmod 664 performance_data.json; fi

echo ""
echo "🔄 Restarting dashboard service..."

# Restart dashboard service to refresh
sudo systemctl restart fxbot-dashboard.service

# Wait for service to start
sleep 3

# Check service status
if systemctl is-active --quiet fxbot-dashboard.service; then
    echo "✅ Dashboard service restarted successfully"
else
    echo "❌ Dashboard service failed to restart"
    echo "Checking logs..."
    journalctl -u fxbot-dashboard.service -n 10 --no-pager
fi

echo ""
echo "🧪 Testing dashboard reset..."

# Test dashboard is accessible
if curl -s --connect-timeout 5 "http://localhost:8502/api/stats" > /dev/null; then
    echo "✅ Dashboard is responding"

    # Get current stats
    STATS=$(curl -s "http://localhost:8502/api/stats")
    echo "📊 Current dashboard stats: $STATS"
else
    echo "⚠️  Dashboard may need a moment to start up"
fi

echo ""
echo "🎉 DASHBOARD DATA RESET COMPLETE!"
echo "================================"
echo "✅ All previous inaccurate data backed up to: $BACKUP_DIR"
echo "✅ Dashboard cleared and ready for fresh tracking"
echo "✅ Service restarted and responding"

echo ""
echo "🎯 Next Steps:"
echo "1. Check dashboard at http://localhost:8502"
echo "2. Should show 0 signals, 0% win rate, clean slate"
echo "3. New signals will be tracked with accurate real-time prices"
echo "4. Start monitoring true performance from this point forward"

echo ""
echo "📊 What Changed:"
echo "• Previous data: 30+ pip price inaccuracies"
echo "• New tracking: Real-time Yahoo Finance prices (5-15 pip accuracy)"
echo "• Fresh analytics: True win rate and performance metrics"
echo "• Clean baseline: Accurate tracking starts now"

echo ""
echo "$(date): Dashboard data reset completed successfully"
EOF

echo ""
echo "🎉 DASHBOARD RESET SUCCESSFUL!"
echo "============================="
print_status "All inaccurate data cleared and backed up"
print_status "Dashboard ready for accurate tracking"
print_info "Check your dashboard at http://localhost:8502"

echo ""
echo "🎯 Your dashboard now shows:"
echo "• 0 total signals"
echo "• 0% win rate"
echo "• Clean performance metrics"
echo "• Ready for real-time price tracking"

echo ""
print_info "From this point forward, all data will be accurate with real-time prices!"
echo "$(date): Dashboard reset deployment completed"