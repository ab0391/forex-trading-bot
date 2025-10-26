#!/bin/bash
# Trading System Startup Script

echo "🚀 Starting ZoneSync Trading System..."
echo "========================================"
echo ""

# Stop any existing processes
echo "🛑 Stopping existing processes..."
pkill -f yahoo_forex_bot 2>/dev/null
pkill -f dashboard_server_mac 2>/dev/null
sleep 2

# Verify trade tracking files exist
echo "📁 Verifying trade tracking system..."
python3 -c "from trade_tracker import TradeTracker; t = TradeTracker(); print('✅ Trade tracker initialized')" || exit 1

# Start the trading bot
echo ""
echo "🤖 Starting trading bot..."
python3 yahoo_forex_bot.py > bot.log 2>&1 &
BOT_PID=$!
sleep 3

# Check if bot started successfully
if ps -p $BOT_PID > /dev/null; then
    echo "   ✅ Trading bot started (PID: $BOT_PID)"
else
    echo "   ❌ Trading bot failed to start"
    echo "   Check bot.log for errors"
    exit 1
fi

# Start the dashboard
echo ""
echo "📊 Starting dashboard..."
python3 dashboard_server_mac.py > dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 2

# Check if dashboard started successfully
if ps -p $DASHBOARD_PID > /dev/null; then
    echo "   ✅ Dashboard started (PID: $DASHBOARD_PID)"
else
    echo "   ❌ Dashboard failed to start"
    echo "   Check dashboard.log for errors"
    exit 1
fi

echo ""
echo "✅ System Started Successfully!"
echo "========================================"
echo ""
echo "📊 Dashboard: http://localhost:5000"
echo "📱 Telegram: Notifications enabled"
echo "🤖 Bot: Running with trade tracking"
echo ""
echo "📋 Quick Commands:"
echo "   • Check status: python3 verify_trade_tracking.py"
echo "   • View bot logs: tail -f bot.log"
echo "   • View dashboard logs: tail -f dashboard.log"
echo "   • Stop system: pkill -f yahoo_forex_bot && pkill -f dashboard_server_mac"
echo ""
echo "🎯 Phase A Features Active:"
echo "   ✅ Signal deduplication (no contradictory signals)"
echo "   ✅ 4-hour cooldown after trade closes"
echo "   ✅ Live price monitoring (every 15 minutes)"
echo "   ✅ Auto stop/target detection"
echo ""
echo "🤖 Phase B Features Active:"
echo "   ✅ AI-powered dynamic R:R (2:1 to 5:1)"
echo "   ✅ ATR volatility analysis"
echo "   ✅ Zone strength scoring"
echo "   ✅ Market momentum tracking"
echo ""
echo "⏳ Monitoring will begin in next market scan cycle..."
echo "Press Ctrl+C anytime to view this message again, or run:"
echo "   ./start_trading_system.sh"

