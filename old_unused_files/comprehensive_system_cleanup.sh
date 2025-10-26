#!/bin/bash

echo "🧹 COMPREHENSIVE SYSTEM CLEANUP & MINIMAL DEPLOYMENT"
echo "======================================================"

# Phase 1: System Investigation and Cleanup
ssh -o ConnectTimeout=60 ubuntu@144.126.254.179 << 'REMOTE_SCRIPT'
set -e

echo "Phase 1: System Investigation and Cleanup"
echo "========================================="

# Audit all running processes
echo "🔍 Auditing all running processes..."
ps aux | grep -E "(python|fxbot)" | grep -v grep || echo "No Python/FXbot processes found"

# Check all systemd services
echo "🔍 Checking all systemd services..."
systemctl list-unit-files | grep fxbot || echo "No FXbot services found"

# Stop ALL potential bot services
echo "🛑 Stopping all potential bot services..."
sudo systemctl stop fxbot-enhanced-watchdog.service 2>/dev/null || echo "fxbot-enhanced-watchdog.service not found"
sudo systemctl stop fxbot-enhanced-watchdog.timer 2>/dev/null || echo "fxbot-enhanced-watchdog.timer not found"
sudo systemctl stop fxbot.service 2>/dev/null || echo "fxbot.service not found"
sudo systemctl stop fxbot.timer 2>/dev/null || echo "fxbot.timer not found"
sudo systemctl stop trading-bot.service 2>/dev/null || echo "trading-bot.service not found"
sudo systemctl stop trading-bot.timer 2>/dev/null || echo "trading-bot.timer not found"

# Disable all bot services
echo "❌ Disabling all bot services..."
sudo systemctl disable fxbot-enhanced-watchdog.service 2>/dev/null || echo "Already disabled"
sudo systemctl disable fxbot-enhanced-watchdog.timer 2>/dev/null || echo "Already disabled"
sudo systemctl disable fxbot.service 2>/dev/null || echo "Already disabled"
sudo systemctl disable fxbot.timer 2>/dev/null || echo "Already disabled"

# Kill any remaining Python processes (be careful!)
echo "💀 Killing any remaining bot processes..."
sudo pkill -f "complete_enhanced_trading_bot" 2>/dev/null || echo "No bot processes to kill"

# Check what bot files exist
echo "📁 Bot files currently on server:"
ls -la /home/ubuntu/fxbot/*.py | grep -E "(trading_bot|enhanced)" || echo "No bot files found"

echo "✅ Phase 1 Complete - System cleaned"
REMOTE_SCRIPT

echo "Phase 1 complete. Now deploying ultra minimal bot..."

# Phase 2: Deploy Ultra Minimal Bot (1 API call per scan)
cat > /tmp/single_call_bot.py << 'EOF'
import time
import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SingleCallTradingBot:
    def __init__(self):
        # ABSOLUTE MINIMAL: Only 1 pair, 1 timeframe = 1 API call per scan
        self.symbol = "EUR/USD"  # Most liquid pair globally
        self.timeframe = "1d"    # Daily only

        # API credentials
        self.api_key = os.getenv("TWELVEDATA_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_market_data(self):
        """Get market data - EXACTLY 1 API call"""
        try:
            self.logger.info("🚀 Making SINGLE API call...")

            url = f"https://api.twelvedata.com/time_series"
            params = {
                "symbol": self.symbol,
                "interval": self.timeframe,
                "outputsize": "10",  # Minimal data
                "apikey": self.api_key
            }

            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                self.logger.info(f"✅ SINGLE API call successful: {self.symbol} {self.timeframe}")
                return response.json()
            else:
                self.logger.error(f"❌ API error: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"❌ API call failed: {e}")
            return None

    def analyze_data(self, data):
        """Simple analysis of the single data point"""
        if not data or 'values' not in data:
            return None

        values = data['values']
        if len(values) < 2:
            return None

        current_price = float(values[0]['close'])
        previous_price = float(values[1]['close'])
        change_pct = ((current_price - previous_price) / previous_price) * 100

        return {
            'symbol': self.symbol,
            'price': current_price,
            'change_pct': change_pct,
            'signal': 'BUY' if change_pct > 1.0 else 'SELL' if change_pct < -1.0 else 'HOLD'
        }

    def send_telegram_notification(self, analysis):
        """Send Telegram notification if signal is strong"""
        if not analysis or analysis['signal'] == 'HOLD':
            return

        try:
            message = f"📊 <b>FX Signal (1 API call)</b>\n\n"
            message += f"Pair: {analysis['symbol']}\n"
            message += f"Price: {analysis['price']:.5f}\n"
            message += f"Change: {analysis['change_pct']:.2f}%\n"
            message += f"Signal: {analysis['signal']}"

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            response = requests.post(url, data=data)
            if response.status_code == 200:
                self.logger.info("✅ Telegram notification sent")
            else:
                self.logger.error(f"❌ Telegram error: {response.status_code}")

        except Exception as e:
            self.logger.error(f"❌ Telegram send failed: {e}")

    def run_single_scan(self):
        """Run complete scan with exactly 1 API call"""
        try:
            scan_start = datetime.now()
            self.logger.info("🤖 SINGLE CALL FX Bot Starting...")

            # Make exactly 1 API call
            data = self.get_market_data()

            if data:
                # Analyze the single data point
                analysis = self.analyze_data(data)

                if analysis:
                    self.logger.info(f"📈 Analysis: {analysis['symbol']} = {analysis['signal']} ({analysis['change_pct']:.2f}%)")

                    # Send notification if signal is strong
                    self.send_telegram_notification(analysis)
                else:
                    self.logger.info("📊 No analysis possible with current data")
            else:
                self.logger.error("❌ Failed to get market data")

            scan_duration = (datetime.now() - scan_start).total_seconds()
            self.logger.info(f"✅ SINGLE CALL scan complete in {scan_duration:.1f}s - Used exactly 1 API credit")

        except Exception as e:
            self.logger.error(f"❌ Scan failed: {e}")
            # Send error notification
            try:
                error_msg = f"❌ FX Bot Error: {str(e)}"
                requests.post(
                    f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                    data={"chat_id": self.telegram_chat_id, "text": error_msg}
                )
            except:
                pass

if __name__ == "__main__":
    bot = SingleCallTradingBot()
    bot.run_single_scan()
EOF

echo "📁 Deploying single call bot..."
scp /tmp/single_call_bot.py ubuntu@144.126.254.179:/home/ubuntu/fxbot/single_call_trading_bot.py

# Phase 3: Create new systemd service
ssh ubuntu@144.126.254.179 << 'SERVICE_SCRIPT'

echo "🔧 Creating new systemd service..."

# Create service file
sudo tee /etc/systemd/system/fxbot-single-call.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=FX Trading Bot Single Call (1 API call per scan)
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
ExecStart=/usr/bin/python3 /home/ubuntu/fxbot/single_call_trading_bot.py
Environment=PATH=/usr/bin:/bin
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Create timer file (every 60 minutes)
sudo tee /etc/systemd/system/fxbot-single-call.timer > /dev/null << 'TIMER_EOF'
[Unit]
Description=Run FX Bot Single Call every 60 minutes
Requires=fxbot-single-call.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=60min
Persistent=true

[Install]
WantedBy=timers.target
TIMER_EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable fxbot-single-call.timer
sudo systemctl start fxbot-single-call.timer

echo "✅ Single call service deployed and started"

# Check status
systemctl status fxbot-single-call.timer --no-pager -l

echo "📊 DEPLOYMENT COMPLETE"
echo "====================="
echo "✅ Only 1 API call per scan (EUR/USD daily)"
echo "✅ Scans every 60 minutes"
echo "✅ Daily usage: 24 calls (3% of 800 limit)"
echo "✅ Rate limit: 1 call per hour (massively under 8/minute)"

SERVICE_SCRIPT

echo "🎯 COMPREHENSIVE CLEANUP AND DEPLOYMENT COMPLETE!"
echo "📊 System now using exactly 1 API call per scan"
echo "📈 Daily usage: 24 calls = 3% of your 800 credit limit"
echo "⏱️  Next scan in ~60 minutes"