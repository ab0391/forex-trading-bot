#!/bin/bash

# Deploy ultra minimal trading bot - only 4 API calls per scan
echo "Deploying ultra minimal trading bot (4 calls per scan)..."

# Create ultra minimal version
cat > /tmp/ultra_minimal_bot.py << 'EOF'
import time
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class UltraMinimalTradingBot:
    def __init__(self):
        # ULTRA MINIMAL: Only 2 most liquid pairs
        self.symbols = [
            "EUR/USD",  # Most liquid pair globally
            "GBP/USD"   # Second most important major
        ]

        # MINIMAL: Only 2 most important timeframes
        self.timeframes = ["1d", "4h"]  # Daily and 4-hour only

        # Total calls per scan: 2 pairs × 2 timeframes = 4 calls

        self.api_key = os.getenv("TWELVEDATA_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_market_data(self, symbol, timeframe):
        """Get market data with rate limiting"""
        try:
            # 10 second delay between calls to be extra safe
            time.sleep(10)

            url = f"https://api.twelvedata.com/time_series"
            params = {
                "symbol": symbol,
                "interval": timeframe,
                "outputsize": "50",
                "apikey": self.api_key
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                self.logger.info(f"✓ API call for {symbol} {timeframe}")
                return response.json()
            else:
                self.logger.error(f"API error for {symbol} {timeframe}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting data for {symbol} {timeframe}: {e}")
            return None

    def analyze_all_pairs(self):
        """Analyze with ultra minimal calls"""
        self.logger.info("🚀 Starting ultra minimal analysis (4 calls only)...")

        analysis_results = {}
        total_calls = 0
        start_time = time.time()

        for symbol in self.symbols:
            analysis_results[symbol] = {}

            for timeframe in self.timeframes:
                total_calls += 1
                self.logger.info(f"📊 Call #{total_calls}/4: {symbol} {timeframe}")

                data = self.get_market_data(symbol, timeframe)

                if data and 'values' in data:
                    values = data['values']
                    if len(values) >= 2:
                        current_price = float(values[0]['close'])
                        previous_price = float(values[1]['close'])
                        change_pct = ((current_price - previous_price) / previous_price) * 100

                        analysis_results[symbol][timeframe] = {
                            'price': current_price,
                            'change_pct': change_pct,
                            'signal': 'BUY' if change_pct > 0.5 else 'SELL' if change_pct < -0.5 else 'HOLD'
                        }
                else:
                    analysis_results[symbol][timeframe] = {'error': 'No data'}

        duration = time.time() - start_time
        self.logger.info(f"✅ ULTRA MINIMAL: {total_calls} API calls in {duration:.1f} seconds")

        return analysis_results

    def send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                self.logger.info("✅ Telegram notification sent")
        except Exception as e:
            self.logger.error(f"Telegram error: {e}")

    def run_analysis(self):
        """Main analysis run - ULTRA MINIMAL"""
        try:
            self.logger.info("🤖 FX Bot ULTRA MINIMAL (4 calls) Starting...")

            # Analyze with only 4 API calls total
            results = self.analyze_all_pairs()

            # Generate summary
            signals = []
            for symbol, timeframes in results.items():
                for tf, data in timeframes.items():
                    if 'signal' in data and data['signal'] in ['BUY', 'SELL']:
                        signals.append(f"{symbol} {tf}: {data['signal']} ({data['change_pct']:.2f}%)")

            if signals:
                message = f"🚨 <b>FX Signals (Minimal)</b> 🚨\n\n" + "\n".join(signals)
                self.send_telegram_message(message)
                self.logger.info(f"Generated {len(signals)} signals with only 4 API calls")
            else:
                self.logger.info("No signals - 4 API calls used")

            self.logger.info("✅ ULTRA MINIMAL scan complete")

        except Exception as e:
            self.logger.error(f"Analysis error: {e}")

if __name__ == "__main__":
    bot = UltraMinimalTradingBot()
    bot.run_analysis()
EOF

# Deploy ultra minimal version
echo "Creating ultra minimal bot file..."
scp /tmp/ultra_minimal_bot.py ubuntu@144.126.254.179:/home/ubuntu/fxbot/complete_enhanced_trading_bot_ultra_minimal.py

# Update service to use ultra minimal version
ssh ubuntu@144.126.254.179 "
cd /home/ubuntu/fxbot
sudo systemctl stop fxbot-enhanced-watchdog.service

# Update service file to use ultra minimal bot
sudo tee /etc/systemd/system/fxbot-enhanced-watchdog.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=FX Trading Bot Ultra Minimal (4 calls only)
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
ExecStart=/usr/bin/python3 /home/ubuntu/fxbot/complete_enhanced_trading_bot_ultra_minimal.py
Environment=PATH=/usr/bin:/bin

[Install]
WantedBy=multi-user.target
SERVICE_EOF

sudo systemctl daemon-reload
sudo systemctl enable fxbot-enhanced-watchdog.service
sudo systemctl start fxbot-enhanced-watchdog.service

echo '✅ Ultra minimal bot deployed!'
echo '📊 Only 4 API calls per scan (2 pairs × 2 timeframes)'
echo '📈 Daily usage: 4 calls × 24 scans = 96 calls (12% of limit)'
echo '🎯 Guaranteed under all limits'
"

echo "🎯 ULTRA MINIMAL DEPLOYMENT COMPLETE"
echo "📊 Only 4 API calls per scan"
echo "📈 Daily: 96 calls (12% of 800 limit)"
echo "⚡ Rate: 4 calls per hour (well under 8/minute)"