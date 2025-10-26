#!/bin/bash

# Fix Systemd Service to Use Optimized Bot
# This script updates the systemd service to call the optimized bot instead of old module

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo -e "${BLUE}"
echo "🔧 Fixing Systemd Service Configuration"
echo "====================================="
echo "Problem: Service calls old 'multi_strategy_trading_tool' module"
echo "Solution: Update to use optimized 'complete_enhanced_trading_bot_fixed.py'"
echo -e "${NC}"

# Step 1: Stop current services
print_info "Stopping current services..."
sudo systemctl stop fxbot-run.service || true
sudo systemctl stop fxbot-enhanced-watchdog.service || true

# Step 2: Update the main service configuration
print_info "Updating fxbot-run.service configuration..."

sudo tee /etc/systemd/system/fxbot-run.service > /dev/null <<SERVICE_EOF
[Unit]
Description=ZoneSync FX Bot - API Credit Optimized
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
Environment=PYTHONPATH=/home/ubuntu/fxbot
ExecStart=/bin/bash -lc 'cd /home/ubuntu/fxbot && source .venv/bin/activate && python complete_enhanced_trading_bot_fixed.py'
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

print_status "Service configuration updated to use optimized bot"

# Step 3: Reload systemd daemon
print_info "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Step 4: Enable and restart services
print_info "Enabling and restarting services..."
sudo systemctl enable fxbot-run.service
sudo systemctl start fxbot-enhanced-watchdog.timer
sudo systemctl restart fxbot-run.service

# Step 5: Verify configuration
print_info "Verifying service configuration..."
echo ""
echo "📋 Service Status:"
systemctl status fxbot-run.service --no-pager || true
echo ""
echo "📋 Timer Status:"
systemctl status fxbot-enhanced-watchdog.timer --no-pager || true

print_status "Systemd service updated to use optimized bot!"
echo ""
echo "🚀 Expected Results:"
echo "• Service now calls: complete_enhanced_trading_bot_fixed.py"
echo "• Optimizations active: caching, Yahoo Finance, reduced sizes"
echo "• API usage should drop to ~400/800 credits"
echo ""
echo "📊 Monitor logs for optimization messages:"
echo "journalctl -u fxbot-run.service -f"
echo ""
echo "Look for:"
echo "✅ 'ZoneSync FX Bot - API Credit Optimized Version'"
echo "✅ 'Yahoo Finance available for current prices'"
echo "✅ 'Cache HIT: EUR/USD 1d (saved API call)'"
echo "✅ 'DataFetcher optimized for API credit reduction'"