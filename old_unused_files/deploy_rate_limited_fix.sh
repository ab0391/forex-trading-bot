#!/bin/bash

# Deploy rate limited trading bot fix
echo "Deploying rate limited trading bot..."

# Create rate limited version with proper API spacing
cat > /tmp/rate_limited_bot.py << 'EOF'
import asyncio
import aiohttp
import time
import json
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class RateLimitedTradingBot:
    def __init__(self):
        # EMERGENCY: Only 4 most important pairs (60% reduction)
        self.symbols = [
            "EUR/USD",  # Most liquid pair
            "GBP/USD",  # Major pair
            "USD/JPY",  # Major pair
            "AUD/USD"   # Commodity pair
        ]

        # Rate limiting: Max 8 calls per minute
        self.api_calls_per_minute = 8
        self.api_call_interval = 60 / self.api_calls_per_minute  # 7.5 seconds between calls

        self.timeframes = ["1d", "4h", "1h"]
        self.api_key = os.getenv("TWELVEDATA_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Virtual trading
        self.balance = 10000.0
        self.positions = {}
        self.trade_history = []

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def get_market_data_with_rate_limit(self, symbol, timeframe):
        """Get market data with rate limiting - 7.5 second delay between calls"""
        try:
            # Wait for rate limit
            await asyncio.sleep(self.api_call_interval)

            url = f"https://api.twelvedata.com/time_series"
            params = {
                "symbol": symbol,
                "interval": timeframe,
                "outputsize": "50",
                "apikey": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"✓ API call for {symbol} {timeframe} - Rate limited")
                        return data
                    else:
                        self.logger.error(f"API error for {symbol} {timeframe}: {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"Error getting data for {symbol} {timeframe}: {e}")
            return None

    async def analyze_all_pairs(self):
        """Analyze all pairs with proper rate limiting"""
        self.logger.info("🚀 Starting rate-limited analysis...")

        analysis_results = {}
        total_calls = 0
        start_time = time.time()

        for symbol in self.symbols:
            analysis_results[symbol] = {}

            for timeframe in self.timeframes:
                self.logger.info(f"📊 Analyzing {symbol} on {timeframe} (Call #{total_calls + 1}/12)")

                data = await self.get_market_data_with_rate_limit(symbol, timeframe)
                total_calls += 1

                if data and 'values' in data:
                    # Simple analysis (price change)
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
        self.logger.info(f"✅ Analysis complete: {total_calls} API calls in {duration:.1f} seconds")

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
            else:
                self.logger.error(f"Telegram error: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Telegram send error: {e}")

    async def run_analysis(self):
        """Main analysis run with rate limiting"""
        try:
            self.logger.info("🤖 FX Bot Rate Limited Analysis Starting...")

            # Analyze all pairs with rate limiting
            results = await self.analyze_all_pairs()

            # Generate summary
            signals = []
            for symbol, timeframes in results.items():
                for tf, data in timeframes.items():
                    if 'signal' in data and data['signal'] in ['BUY', 'SELL']:
                        signals.append(f"{symbol} {tf}: {data['signal']} ({data['change_pct']:.2f}%)")

            if signals:
                message = f"🚨 <b>FX Trading Signals</b> 🚨\n\n" + "\n".join(signals[:5])
                self.send_telegram_message(message)
                self.logger.info(f"Generated {len(signals)} trading signals")
            else:
                self.logger.info("No strong signals generated")

        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            self.send_telegram_message(f"❌ Trading bot error: {str(e)}")

if __name__ == "__main__":
    bot = RateLimitedTradingBot()
    asyncio.run(bot.run_analysis())
EOF

# Copy to server
scp /tmp/rate_limited_bot.py ubuntu@144.126.254.179:/home/ubuntu/fxbot/complete_enhanced_trading_bot_rate_limited.py

# Update the service to use rate limited version
ssh ubuntu@144.126.254.179 "
cd /home/ubuntu/fxbot
sudo systemctl stop fxbot-enhanced-watchdog.service
sudo tee /etc/systemd/system/fxbot-enhanced-watchdog.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=FX Trading Bot Enhanced Watchdog (Rate Limited)
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/fxbot
ExecStart=/usr/bin/python3 /home/ubuntu/fxbot/complete_enhanced_trading_bot_rate_limited.py
Environment=PATH=/usr/bin:/bin

[Install]
WantedBy=multi-user.target
SERVICE_EOF

sudo systemctl daemon-reload
sudo systemctl enable fxbot-enhanced-watchdog.service
sudo systemctl start fxbot-enhanced-watchdog.service
echo 'Rate limited bot deployed successfully!'
"

echo "✅ Rate limited trading bot deployed!"
echo "📊 Now using 7.5 second delays between API calls"
echo "⏱️  Total scan time: ~90 seconds (12 calls × 7.5s)"
echo "🎯 Respects 8 calls/minute limit"