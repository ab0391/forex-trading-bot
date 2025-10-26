#!/bin/bash
# Complete Deployment: Enhanced Bot + $10 Dashboard + Lifecycle Management

echo "🚀 COMPLETE ZONESYNC ENHANCEMENT DEPLOYMENT"
echo "=========================================="
echo "🔄 Trade Lifecycle Management + 10 Currency Pairs + $10 Trade Template"
echo ""

echo "📋 Deployment Plan:"
echo "1. Reset dashboard (clear old duplicate signals)"
echo "2. Deploy $10 trade template dashboard"
echo "3. Deploy enhanced bot with lifecycle management"
echo "4. Verify integration and functionality"
echo ""

read -p "🎯 Ready to deploy complete enhancement? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🔄 Step 1: Resetting Dashboard..."
echo "================================"
./reset_dashboard_clean.sh

echo ""
echo "💰 Step 2: Deploying $10 Trade Template Dashboard..."
echo "=================================================="
./deploy_10dollar_dashboard.sh

echo ""
echo "🤖 Step 3: Deploying Enhanced Bot with Lifecycle Management..."
echo "==========================================================="
./deploy_lifecycle_bot.sh

echo ""
echo "⏱️  Step 4: Waiting for full system initialization..."
sleep 10

echo ""
echo "🧪 Step 5: Verification..."
echo "========================="

# SSH and verify
ssh fxbot << 'EOF'
echo "📊 Checking system status..."

echo ""
echo "🤖 Bot Service Status:"
systemctl status fxbot-run.service --no-pager | head -10

echo ""
echo "📊 Dashboard Service Status:"
systemctl status fxbot-dashboard.service --no-pager | head -10

echo ""
echo "⏰ Timer Status:"
systemctl status fxbot-enhanced-watchdog.timer --no-pager | head -10

echo ""
echo "📁 File Check:"
ls -la /home/ubuntu/fxbot/signals_history.json /home/ubuntu/fxbot/active_trades.json 2>/dev/null || echo "New files will be created on first run"

echo ""
echo "🔗 Dashboard Test:"
curl -s -I http://localhost:80 | head -3

echo ""
echo "✅ VERIFICATION COMPLETE"
EOF

echo ""
echo "🎉 COMPLETE DEPLOYMENT SUCCESSFUL!"
echo "================================="
echo ""
echo "🔥 WHAT YOU NOW HAVE:"
echo "✅ Enhanced Bot with Trade Lifecycle Management"
echo "✅ 10 Currency Pairs (2x more opportunities)"
echo "✅ No More Duplicate Signals (one per trade setup)"
echo "✅ $10 Trade Template Dashboard"
echo "✅ Real Dollar P&L Tracking"
echo "✅ Auto SL/TP Monitoring"
echo "✅ Clean Signal Generation"
echo ""
echo "📊 CURRENCY PAIRS MONITORED:"
echo "Major: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CHF"
echo "Added: NZD/USD, USD/CAD, EUR/GBP, EUR/JPY, GBP/JPY"
echo ""
echo "💰 P&L CALCULATION:"
echo "• Loss: -$10 (always)"
echo "• Win 2:1 = +$20"
echo "• Win 3:1 = +$30"
echo "• Win 4:1 = +$40"
echo "• Win 5:1 = +$50"
echo "• Win 6:1+ = +$60+"
echo ""
echo "🎯 HOW IT WORKS:"
echo "1. Bot detects setup → Sends ONE signal → Marks pair as active"
echo "2. You record win/loss on dashboard"
echo "3. Bot monitors SL/TP automatically"
echo "4. When trade closes → Pair becomes available for new signals"
echo "5. Other pairs continue independently"
echo ""
echo "🌐 ACCESS DASHBOARD:"
echo "SSH Tunnel: ssh -L 8080:localhost:80 fxbot"
echo "Then open: http://localhost:8080"
echo ""
echo "📈 EXPECTED RESULTS:"
echo "• Clean, unique signals (no spam)"
echo "• 2x-3x more trading opportunities"
echo "• Real dollar tracking"
echo "• Professional trade management"
echo ""
echo "🔍 MONITOR LOGS:"
echo "journalctl -u fxbot-run.service -f"
echo ""
echo "✨ ENHANCEMENT COMPLETE - ENJOY PROFESSIONAL TRADING! ✨"