#!/bin/bash

echo "🚨 EMERGENCY SINGLE CALL DEPLOYMENT"
echo "===================================="
echo "This script creates an ultra-minimal bot that makes exactly 1 API call per scan"
echo "Daily usage: 24 calls = 3% of your 800 credit limit"
echo ""

# Create the ultra-minimal single call bot
cat > single_call_trading_bot.py << 'EOF'
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
            format='%(asctime)s - SINGLE_CALL_BOT - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_market_data(self):
        """Get market data - EXACTLY 1 API call"""
        try:
            self.logger.info("🚀 Making SINGLE API call...")
            call_start = datetime.now()

            url = f"https://api.twelvedata.com/time_series"
            params = {
                "symbol": self.symbol,
                "interval": self.timeframe,
                "outputsize": "5",  # Minimal data needed
                "apikey": self.api_key
            }

            response = requests.get(url, params=params, timeout=30)
            call_duration = (datetime.now() - call_start).total_seconds()

            if response.status_code == 200:
                self.logger.info(f"✅ SINGLE API call successful in {call_duration:.2f}s: {self.symbol} {self.timeframe}")
                return response.json()
            else:
                self.logger.error(f"❌ API error {response.status_code} in {call_duration:.2f}s")
                return None

        except Exception as e:
            self.logger.error(f"❌ API call failed: {e}")
            return None

    def analyze_data(self, data):
        """Simple analysis of the single data point"""
        if not data or 'values' not in data:
            self.logger.warning("⚠️ No valid data received")
            return None

        values = data['values']
        if len(values) < 2:
            self.logger.warning("⚠️ Insufficient data points for analysis")
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
        if not analysis:
            return

        try:
            # Always send a status update (even for HOLD signals)
            if analysis['signal'] != 'HOLD':
                message = f"🚨 <b>FX Signal (1 API call)</b>\n\n"
                message += f"Pair: {analysis['symbol']}\n"
                message += f"Price: {analysis['price']:.5f}\n"
                message += f"Change: {analysis['change_pct']:+.2f}%\n"
                message += f"Signal: {analysis['signal']}\n\n"
                message += f"⚡ Used exactly 1 API credit"
            else:
                # Send periodic status update for HOLD signals (every 4 hours)
                hour = datetime.now().hour
                if hour % 4 == 0 and datetime.now().minute < 5:  # Only at top of 4-hour intervals
                    message = f"📊 <b>FX Status (1 API call)</b>\n\n"
                    message += f"Pair: {analysis['symbol']}\n"
                    message += f"Price: {analysis['price']:.5f}\n"
                    message += f"Change: {analysis['change_pct']:+.2f}%\n"
                    message += f"Status: Market stable\n\n"
                    message += f"⚡ Used exactly 1 API credit"
                else:
                    return  # Skip HOLD notifications except every 4 hours

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            response = requests.post(url, data=data, timeout=10)
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
            self.logger.info(f"📊 Target: {self.symbol} {self.timeframe} - 1 API call only")

            # Make exactly 1 API call
            data = self.get_market_data()

            if data:
                # Analyze the single data point
                analysis = self.analyze_data(data)

                if analysis:
                    self.logger.info(f"📈 Analysis: {analysis['symbol']} = {analysis['signal']} ({analysis['change_pct']:+.2f}%)")

                    # Send notification
                    self.send_telegram_notification(analysis)
                else:
                    self.logger.warning("⚠️ No analysis possible with current data")
            else:
                self.logger.error("❌ Failed to get market data")
                # Send error notification
                try:
                    error_msg = f"❌ FX Bot: Failed to get market data (used 1 API credit attempting)"
                    requests.post(
                        f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                        data={"chat_id": self.telegram_chat_id, "text": error_msg},
                        timeout=10
                    )
                except:
                    pass

            scan_duration = (datetime.now() - scan_start).total_seconds()
            self.logger.info(f"✅ SINGLE CALL scan complete in {scan_duration:.1f}s")
            self.logger.info("⚡ Used exactly 1 API credit (target: 24/day = 3% of limit)")

        except Exception as e:
            self.logger.error(f"❌ Scan failed: {e}")
            # Send error notification
            try:
                error_msg = f"❌ FX Bot Critical Error: {str(e)}"
                requests.post(
                    f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                    data={"chat_id": self.telegram_chat_id, "text": error_msg},
                    timeout=10
                )
            except:
                pass

if __name__ == "__main__":
    print("🚀 Starting Single Call Trading Bot...")
    print("📊 EUR/USD Daily analysis - 1 API call per scan")
    print("⚡ Target usage: 24 calls/day = 3% of 800 credit limit")
    print("=" * 50)

    bot = SingleCallTradingBot()
    bot.run_single_scan()
EOF

# Create systemd service file
cat > fxbot-single-call.service << 'EOF'
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
EOF

# Create systemd timer file
cat > fxbot-single-call.timer << 'EOF'
[Unit]
Description=Run FX Bot Single Call every 60 minutes
Requires=fxbot-single-call.service

[Timer]
OnBootSec=3min
OnUnitActiveSec=60min
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo "✅ Files created successfully!"
echo ""
echo "📁 Files created:"
echo "  • single_call_trading_bot.py (1 API call per scan)"
echo "  • fxbot-single-call.service (systemd service)"
echo "  • fxbot-single-call.timer (60-minute intervals)"
echo ""
echo "🚀 To deploy manually (if SSH is available):"
echo "1. Copy single_call_trading_bot.py to /home/ubuntu/fxbot/"
echo "2. Copy service files to /etc/systemd/system/"
echo "3. Run: sudo systemctl daemon-reload"
echo "4. Run: sudo systemctl enable fxbot-single-call.timer"
echo "5. Run: sudo systemctl start fxbot-single-call.timer"
echo ""
echo "📊 Expected results:"
echo "  • 1 API call per scan (EUR/USD daily)"
echo "  • 24 scans per day = 24 API calls"
echo "  • 3% usage of 800 credit limit"
echo "  • Massive improvement from current 12-27 calls per scan"