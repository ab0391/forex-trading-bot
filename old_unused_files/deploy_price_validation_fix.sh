#!/bin/bash
# Deploy Price Validation Fix to ZoneSync Trading Bot
# Fixes the issue where entry prices are 300+ pips away from current market price

set -e

echo "🔧 ZoneSync Price Validation Fix Deployment"
echo "=========================================="
echo "$(date): Starting price validation fix deployment"

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

# Check if we're in the right directory
if [[ ! -f "complete_enhanced_trading_bot_fixed.py" ]]; then
    print_error "complete_enhanced_trading_bot_fixed.py not found"
    echo "Please run this script from the Trading Bot directory"
    exit 1
fi

echo "🔍 Checking source file..."
if [[ -f "complete_enhanced_trading_bot_fixed.py" ]]; then
    print_status "Price-validated bot file found"
else
    print_error "Source file missing: complete_enhanced_trading_bot_fixed.py"
    exit 1
fi

# Step 1: Create backup of current multi_strategy_trading_tool.py if it exists
echo "📦 Creating backup..."
if [[ -f "multi_strategy_trading_tool.py" ]]; then
    cp multi_strategy_trading_tool.py "multi_strategy_trading_tool_$(date +%Y%m%d_%H%M%S).py"
    print_status "Backup created"
else
    print_info "No existing multi_strategy_trading_tool.py to backup"
fi

# Step 2: Copy the price-validated bot to the deployment filename
echo "🚀 Deploying price validation fix..."
cp complete_enhanced_trading_bot_fixed.py multi_strategy_trading_tool.py
print_status "Price-validated bot deployed as multi_strategy_trading_tool.py"

# Step 3: Verify the deployment
echo "🧪 Verifying deployment..."
if [[ -f "multi_strategy_trading_tool.py" ]]; then
    # Check if the price validation function exists
    if grep -q "get_current_price" multi_strategy_trading_tool.py; then
        print_status "Price validation function found"
    else
        print_error "Price validation function missing"
        exit 1
    fi

    # Check if proximity validation exists
    if grep -q "price_distance.*max_distance" multi_strategy_trading_tool.py; then
        print_status "Price proximity validation found"
    else
        print_error "Price proximity validation missing"
        exit 1
    fi

    # Check syntax
    if python3 -m py_compile multi_strategy_trading_tool.py; then
        print_status "Python syntax validated"
    else
        print_error "Python syntax error detected"
        exit 1
    fi
else
    print_error "Deployment failed - file not created"
    exit 1
fi

echo ""
echo "🎉 PRICE VALIDATION FIX DEPLOYED SUCCESSFULLY!"
echo "=============================================="
print_status "Trading bot with price validation is ready for upload"

echo ""
echo "📋 What was fixed:"
echo "• Added real-time price fetching from TwelveData"
echo "• Only alerts zones within 100 pips of current market price"
echo "• Filters out stale zones older than 4 hours"
echo "• Shows current price vs entry price in Telegram alerts"
echo "• Enhanced logging for zone filtering transparency"

echo ""
echo "🚀 Next Steps:"
echo "1. Upload multi_strategy_trading_tool.py to your Oracle server:"
echo "   scp multi_strategy_trading_tool.py fxbot:/home/ubuntu/fxbot/"
echo ""
echo "2. SSH into your server and restart the bot:"
echo "   ssh fxbot"
echo "   cd /home/ubuntu/fxbot"
echo "   sudo systemctl restart fxbot-run.service"
echo ""
echo "3. Monitor the logs to see the fix working:"
echo "   journalctl -u fxbot-run.service -f"
echo ""
echo "4. Look for these log messages:"
echo "   • 'Zone validated: EURUSD entry 1.36120 close to current 1.36055'"
echo "   • 'Zone filtered: EURUSD entry too far from current price'"
echo ""
echo "🎯 Expected Results:"
echo "• No more alerts with 300+ pip price differences"
echo "• Entry prices within 100 pips of current market"
echo "• Telegram alerts showing current vs entry price"
echo "• More relevant and timely trading signals"

echo ""
print_info "The fix is ready to deploy to your Oracle server!"
echo "$(date): Price validation fix deployment completed"