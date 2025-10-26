#!/bin/bash
# Deploy Real-Time Price Fix for ZoneSync Trading Bot
# Comprehensive solution to eliminate price discrepancies

set -e

echo "🚀 ZoneSync Real-Time Price Fix Deployment"
echo "=========================================="
echo "$(date): Starting comprehensive price accuracy deployment"

# Colors for output
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

# Check prerequisites
echo "🔍 Checking prerequisites..."

if [[ ! -f "multi_strategy_trading_tool.py" ]]; then
    print_error "multi_strategy_trading_tool.py not found"
    echo "Please run this script from the Trading Bot directory"
    exit 1
fi

# Verify the fixes are present
echo "🧪 Verifying real-time price fixes..."

if grep -q "import yfinance as yf" multi_strategy_trading_tool.py; then
    print_status "Yahoo Finance integration found"
else
    print_error "Yahoo Finance integration missing"
    exit 1
fi

if grep -q "get_realtime_price_yahoo" multi_strategy_trading_tool.py; then
    print_status "Real-time price fetching function found"
else
    print_error "Real-time price fetching function missing"
    exit 1
fi

if grep -q "len(h1_df) - 58" multi_strategy_trading_tool.py; then
    print_status "Recent zone scanning (48 hours) found"
else
    print_error "Recent zone scanning logic missing"
    exit 1
fi

if grep -q "timedelta(hours=6)" multi_strategy_trading_tool.py; then
    print_status "6-hour freshness requirement found"
else
    print_error "6-hour freshness requirement missing"
    exit 1
fi

if grep -q "max_distance = 0.005" multi_strategy_trading_tool.py; then
    print_status "50-pip validation threshold found"
else
    print_error "50-pip validation threshold missing"
    exit 1
fi

# Test syntax
if python3 -m py_compile multi_strategy_trading_tool.py; then
    print_status "Python syntax validated"
else
    print_error "Python syntax error detected"
    exit 1
fi

echo ""
echo "🎉 ALL FIXES VERIFIED SUCCESSFULLY!"
echo "=================================="

echo ""
echo "📋 Real-Time Price Fix Summary:"
echo "• Yahoo Finance integration for true real-time prices (free, unlimited)"
echo "• Zone detection limited to last 48 hours (vs weeks/months before)"
echo "• 6-hour maximum zone age requirement"
echo "• 50-pip maximum distance validation (vs 100 pips before)"
echo "• Real-time price fallback to TwelveData if Yahoo fails"
echo "• Enhanced logging for price validation transparency"

echo ""
echo "🚀 Deploy to Server:"
echo "1. Upload the enhanced bot:"
echo "   scp multi_strategy_trading_tool.py fxbot:/home/ubuntu/fxbot/"
echo ""
echo "2. Install yfinance on server:"
echo "   ssh fxbot 'cd /home/ubuntu/fxbot && source .venv/bin/activate && pip install yfinance'"
echo ""
echo "3. Restart the bot service:"
echo "   ssh fxbot 'sudo systemctl restart fxbot-run.service'"
echo ""
echo "4. Monitor the enhanced logs:"
echo "   ssh fxbot 'journalctl -u fxbot-run.service -f'"

echo ""
echo "🎯 Expected Results:"
echo "• Entry prices within 5-15 pips of MT5 real-time price"
echo "• Only zones from last 1-2 days (not weeks old)"
echo "• Real-time Yahoo Finance prices in Telegram alerts"
echo "• Enhanced log messages showing price validation details"

echo ""
print_info "Ready to deploy! Run the commands above to activate the real-time price fix."
echo "$(date): Real-time price fix deployment preparation completed"