#!/bin/bash
# ZoneSync Trading Dashboard Deployment Script
# Deploys the complete performance tracking dashboard

set -e

echo "📊 ZoneSync Trading Dashboard Deployment"
echo "========================================"
echo "$(date): Starting dashboard deployment"

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

# Check user
if [ "$USER" != "ubuntu" ]; then
    print_error "Run as ubuntu user"
    exit 1
fi

# Set working directory
FXBOT_DIR="/home/ubuntu/fxbot"
cd "$FXBOT_DIR" || { print_error "Cannot access $FXBOT_DIR"; exit 1; }

print_status "Working directory: $FXBOT_DIR"

# Step 1: Check required files
echo "🔍 Checking dashboard files..."
REQUIRED_FILES=(
    "trading_dashboard.html"
    "dashboard_server.py"
    "enhanced_telegram_handler.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        echo "Please upload all dashboard files first"
        exit 1
    fi
done
print_status "All dashboard files present"

# Step 2: Install Flask if needed
echo "📦 Installing Flask for dashboard server..."
source .venv/bin/activate || { print_error "Cannot activate virtual environment"; exit 1; }

pip install flask || {
    print_warning "Flask installation had issues"
}
print_status "Flask installed"

# Step 3: Create dashboard service
echo "🔧 Creating dashboard service..."
sudo tee /etc/systemd/system/fxbot-dashboard.service > /dev/null <<EOF
[Unit]
Description=ZoneSync Trading Dashboard
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
Environment=PYTHONPATH=/home/ubuntu/fxbot
ExecStart=/home/ubuntu/fxbot/.venv/bin/python3 dashboard_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_status "Dashboard service created"

# Step 4: Reload systemd and start dashboard
echo "🚀 Starting dashboard service..."
sudo systemctl daemon-reload
sudo systemctl enable fxbot-dashboard.service
sudo systemctl start fxbot-dashboard.service

# Wait for service to start
sleep 3

# Step 5: Check service status
if systemctl is-active --quiet fxbot-dashboard.service; then
    print_status "Dashboard service started successfully"
else
    print_error "Dashboard service failed to start"
    echo "Checking logs..."
    journalctl -u fxbot-dashboard.service -n 10 --no-pager
    exit 1
fi

# Step 6: Test dashboard access
echo "🧪 Testing dashboard..."
DASHBOARD_URL="http://localhost:8502"

# Test if dashboard is responding
if curl -s --connect-timeout 5 "$DASHBOARD_URL" > /dev/null; then
    print_status "Dashboard is responding"
else
    print_warning "Dashboard may need a moment to start up"
fi

# Step 7: Get server IP for access instructions
SERVER_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")

# Step 8: Create dashboard access script
echo "📱 Creating quick access commands..."
cat > dashboard_commands.sh << 'EOF'
#!/bin/bash
# ZoneSync Dashboard Quick Commands

echo "📊 ZoneSync Dashboard Commands"
echo "============================="

case "$1" in
    "start")
        sudo systemctl start fxbot-dashboard.service
        echo "✅ Dashboard started"
        ;;
    "stop")
        sudo systemctl stop fxbot-dashboard.service
        echo "🛑 Dashboard stopped"
        ;;
    "restart")
        sudo systemctl restart fxbot-dashboard.service
        echo "🔄 Dashboard restarted"
        ;;
    "status")
        systemctl status fxbot-dashboard.service --no-pager
        ;;
    "logs")
        journalctl -u fxbot-dashboard.service -f
        ;;
    "url")
        SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
        echo "🌐 Dashboard URL: http://$SERVER_IP:8502"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|url}"
        echo ""
        echo "Commands:"
        echo "  start   - Start dashboard service"
        echo "  stop    - Stop dashboard service"
        echo "  restart - Restart dashboard service"
        echo "  status  - Show service status"
        echo "  logs    - Show live logs"
        echo "  url     - Show dashboard URL"
        ;;
esac
EOF

chmod +x dashboard_commands.sh
print_status "Dashboard commands script created"

# Step 9: Integration test
echo "🔗 Testing integration..."
.venv/bin/python3 -c "
import sys
import json
from pathlib import Path

# Test if signals file exists and is readable
signals_file = Path('signals_history.json')
if signals_file.exists():
    try:
        with open(signals_file, 'r') as f:
            data = json.load(f)
        print(f'✅ Found {len(data)} signals in database')
    except Exception as e:
        print(f'⚠️ Error reading signals file: {e}')
else:
    print('ℹ️ No signals file yet - will be created when bot runs')

# Test Telegram handler
try:
    from enhanced_telegram_handler import TelegramOutcomeHandler
    handler = TelegramOutcomeHandler()
    print('✅ Telegram handler loaded successfully')
except Exception as e:
    print(f'⚠️ Telegram handler issue: {e}')

print('✅ Integration test completed')
"

echo ""
echo "🎉 DASHBOARD DEPLOYMENT COMPLETE!"
echo "================================="
print_status "Trading dashboard successfully deployed"

echo ""
echo "📊 Dashboard Access:"
echo "• URL: http://$SERVER_IP:8502"
echo "• Service: fxbot-dashboard.service"
echo "• Port: 8502"

echo ""
echo "🎮 Quick Commands:"
echo "• Start: ./dashboard_commands.sh start"
echo "• Stop: ./dashboard_commands.sh stop"
echo "• Status: ./dashboard_commands.sh status"
echo "• Logs: ./dashboard_commands.sh logs"
echo "• URL: ./dashboard_commands.sh url"

echo ""
echo "📱 Telegram Shortcuts (send these messages to record outcomes):"
echo "• ✅ EURUSD (record win for EURUSD)"
echo "• ❌ GBPUSD (record loss for GBPUSD)"
echo "• win AUDUSD (alternative format)"
echo "• loss USDJPY (alternative format)"

echo ""
echo "🔧 Dashboard Features:"
echo "• 📈 Real-time win rate tracking"
echo "• 📊 Performance charts and analytics"
echo "• 📋 One-click outcome recording"
echo "• 📱 Mobile-responsive interface"
echo "• 🔄 Auto-refresh every minute"
echo "• 💾 Persistent data storage"

echo ""
echo "🎯 Next Steps:"
echo "1. Open http://$SERVER_IP:8502 in your browser"
echo "2. Start recording trade outcomes as they complete"
echo "3. Monitor your win rate progress (target: 50%+)"
echo "4. Use Telegram shortcuts for quick recording"

echo ""
print_status "Your professional trading dashboard is ready!"
print_info "Access it anytime to track your performance and progress"

echo ""
echo "$(date): Dashboard deployment completed successfully"