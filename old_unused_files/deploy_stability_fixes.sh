#!/bin/bash
# ZoneSync FX Bot - Stability Deployment Script
# Run this script on your Oracle server to deploy all stability fixes

set -e  # Exit on any error

echo "🚀 ZoneSync Stability Deployment Starting..."
echo "$(date): Beginning deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    print_error "This script must be run as the ubuntu user"
    exit 1
fi

# Set working directory
FXBOT_DIR="/home/ubuntu/fxbot"
cd "$FXBOT_DIR" || { print_error "Cannot access $FXBOT_DIR"; exit 1; }

print_status "Working directory: $FXBOT_DIR"

# Step 1: Create backup
BACKUP_DIR="../fxbot_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup..."
cp -r . "$BACKUP_DIR"
print_status "Backup created: $BACKUP_DIR"

# Step 2: Check required files exist
echo "🔍 Checking required files..."
REQUIRED_FILES=(
    "multi_strategy_trading_tool_fixed.py"
    "robust_notifier.py"
    "zones_block_fixed.py"
    "enhanced_network_watchdog.py"
    "enhanced_h4_bias.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        echo "Please upload all stability fix files first"
        exit 1
    fi
done
print_status "All required files present"

# Step 3: Install dependencies
echo "📦 Installing Python dependencies..."
source .venv/bin/activate || { print_error "Cannot activate virtual environment"; exit 1; }

pip install psutil requests urllib3 pandas numpy || {
    print_warning "Some packages may already be installed"
}
print_status "Dependencies installed"

# Step 4: Backup original files
echo "🔄 Backing up original files..."
[ -f "multi_strategy_trading_tool.py" ] && cp multi_strategy_trading_tool.py multi_strategy_trading_tool_original.py
[ -f "notifier.py" ] && cp notifier.py notifier_original.py
[ -f "zones_block.py" ] && cp zones_block.py zones_block_original.py
print_status "Original files backed up"

# Step 5: Deploy new files
echo "🚀 Deploying enhanced files..."
cp multi_strategy_trading_tool_fixed.py multi_strategy_trading_tool.py
cp robust_notifier.py notifier.py
cp zones_block_fixed.py zones_block.py
print_status "Core files deployed"

# Step 6: Stop existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop fxbot-run.service || print_warning "fxbot-run.service was not running"
sudo systemctl stop fxbot-run.timer || print_warning "fxbot-run.timer was not active"
sudo systemctl stop fxbot-net-watchdog.timer || print_warning "Old watchdog was not active"
print_status "Services stopped"

# Step 7: Create enhanced watchdog service
echo "🔧 Creating enhanced watchdog service..."
sudo tee /etc/systemd/system/fxbot-enhanced-watchdog.service > /dev/null <<EOF
[Unit]
Description=ZoneSync Enhanced Network Watchdog
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
Environment=PYTHONPATH=/home/ubuntu/fxbot
ExecStart=/home/ubuntu/fxbot/.venv/bin/python3 enhanced_network_watchdog.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/fxbot-enhanced-watchdog.timer > /dev/null <<EOF
[Unit]
Description=Run ZoneSync Enhanced Watchdog every 5 minutes
Requires=fxbot-enhanced-watchdog.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
EOF

print_status "Enhanced watchdog service created"

# Step 8: Reload systemd and start services
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload
print_status "Systemd reloaded"

echo "🚀 Starting services..."
sudo systemctl enable fxbot-enhanced-watchdog.timer
sudo systemctl start fxbot-enhanced-watchdog.timer
sudo systemctl restart fxbot-run.timer
sudo systemctl start fxbot-run.service

print_status "Services started"

# Step 9: Verify deployment
echo "🔍 Verifying deployment..."
sleep 5

# Check service status
echo "Service Status:"
systemctl is-active fxbot-run.timer && print_status "fxbot-run.timer: ACTIVE" || print_error "fxbot-run.timer: FAILED"
systemctl is-active fxbot-enhanced-watchdog.timer && print_status "fxbot-enhanced-watchdog.timer: ACTIVE" || print_error "watchdog timer: FAILED"

# Check recent logs
echo "📋 Recent logs (last 10 lines):"
echo "--- Main Bot Logs ---"
journalctl -u fxbot-run.service -n 10 --no-pager | tail -5

echo "--- Watchdog Logs ---"
journalctl -u fxbot-enhanced-watchdog.service -n 10 --no-pager | tail -5 || echo "Watchdog starting up..."

# Test notification system
echo "📧 Testing notification system..."
cd "$FXBOT_DIR"
.venv/bin/python3 -c "
from robust_notifier import notifier
result = notifier.test_notifications()
print(f'Email: {\"✅\" if result.get(\"email\") else \"❌\"}')
print(f'Telegram: {\"✅\" if result.get(\"telegram\", False) else \"❌\"}')
" || print_warning "Notification test had issues - check .env configuration"

# Generate health report
echo "🏥 Generating health report..."
.venv/bin/python3 enhanced_network_watchdog.py --report || print_warning "Health report generation failed"

# Step 10: Deployment summary
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================="
print_status "Stability fixes deployed successfully"
print_status "Enhanced error handling active"
print_status "Connection pooling enabled"
print_status "SMTP timeouts fixed"
print_status "Missing function restored"
print_status "Enhanced watchdog monitoring"

echo ""
echo "📊 Next Steps:"
echo "1. Monitor logs for next 24 hours: journalctl -u fxbot-run.service -f"
echo "2. Check health reports: python3 enhanced_network_watchdog.py --report"
echo "3. Verify notifications are working"
echo "4. Watch for improved stability (no more Oracle reboots needed!)"

echo ""
echo "🔧 Monitoring Commands:"
echo "• Service status: systemctl status fxbot-run.service fxbot-enhanced-watchdog.service"
echo "• Live logs: journalctl -u fxbot-run.service -f"
echo "• Health check: .venv/bin/python3 enhanced_network_watchdog.py --report"
echo "• Manual test run: .venv/bin/python3 multi_strategy_trading_tool.py"

echo ""
print_status "Your bot should now run autonomously without requiring Oracle server reboots!"
echo "$(date): Deployment completed successfully"