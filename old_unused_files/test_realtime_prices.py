#!/usr/bin/env python3
"""
Real-Time Price Test for ZoneSync Bot
Tests Yahoo Finance price accuracy vs MT5 by sending fake alerts
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import requests

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# For real-time price data
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.error("yfinance not installed. Install with: pip install yfinance")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

class RealTimePriceTester:
    """Test real-time price fetching and Telegram alerts"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token or not self.chat_id:
            logger.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing from environment")
            sys.exit(1)

    def get_yahoo_price(self, symbol: str) -> float:
        """Get real-time price from Yahoo Finance"""

        # Convert to Yahoo Finance format
        yahoo_symbols = {
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X",
            "USD/JPY": "USDJPY=X",
            "AUD/USD": "AUDUSD=X",
            "USD/CHF": "USDCHF=X"
        }

        yahoo_symbol = yahoo_symbols.get(symbol, f"{symbol.replace('/', '')}=X")

        try:
            ticker = yf.Ticker(yahoo_symbol)

            # Try multiple methods
            try:
                # Method 1: fast_info
                price = float(ticker.fast_info.last_price)
                if price and price > 0:
                    return price
            except:
                pass

            try:
                # Method 2: info
                info = ticker.info
                if 'regularMarketPrice' in info and info['regularMarketPrice']:
                    return float(info['regularMarketPrice'])
            except:
                pass

            try:
                # Method 3: history
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    return float(hist['Close'].iloc[-1])
            except:
                pass

            logger.error(f"Could not fetch price for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None

    def send_test_alert(self, symbol: str, current_price: float):
        """Send test Telegram alert"""

        # Create fake entry 5-10 pips away for testing
        if "JPY" in symbol:
            pip_value = 0.01  # JPY pairs
            fake_entry = current_price - 0.05  # 5 pips below
        else:
            pip_value = 0.0001  # Major pairs
            fake_entry = current_price - 0.0005  # 5 pips below

        distance = abs(current_price - fake_entry) / pip_value

        direction = "🟢 LONG"

        message = f"""
🧪 *PRICE TEST ALERT* 🧪

📊 *{symbol}* | {direction}
⚡ *Strategy:* Real-Time Price Test
💰 *Current Price:* `{current_price:.5f}`
📏 *Distance to Entry:* {distance:.1f} pips below

📈 *Test Setup:*
• Entry: `{fake_entry:.5f}`
• Current: `{current_price:.5f}`
• Difference: `{distance:.1f} pips`

🎯 *Compare this price to your MT5!*

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

💡 *This is a test alert to verify price accuracy*
        """.strip()

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"✅ Test alert sent for {symbol}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send test alert for {symbol}: {e}")
            return False

    def test_all_pairs(self):
        """Test all major forex pairs"""

        pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]

        print("🧪 YAHOO FINANCE REAL-TIME PRICE TEST")
        print("=" * 50)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()

        success_count = 0

        for symbol in pairs:
            print(f"📊 Testing {symbol}...")

            # Get real-time price
            price = self.get_yahoo_price(symbol)

            if price:
                print(f"   💰 Yahoo Finance Price: {price:.5f}")

                # Send test alert
                if self.send_test_alert(symbol, price):
                    success_count += 1
                    print(f"   ✅ Test alert sent to Telegram")
                else:
                    print(f"   ❌ Failed to send alert")
            else:
                print(f"   ❌ Failed to fetch price")

            print()

        print("=" * 50)
        print(f"🎯 RESULTS: {success_count}/{len(pairs)} pairs tested successfully")
        print()
        print("📱 CHECK YOUR TELEGRAM for test alerts!")
        print("🔍 COMPARE the prices shown to your MT5")
        print("✅ Prices should be within 5-15 pips of MT5")
        print()
        print("💡 This test shows exactly what your bot sees vs real market")

def main():
    """Run the real-time price test"""

    print("🚀 Starting ZoneSync Real-Time Price Test...")
    print()

    # Check environment
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        print("💡 Make sure your .env file is configured")
        return

    if not os.getenv("TELEGRAM_CHAT_ID"):
        print("❌ TELEGRAM_CHAT_ID not found in environment")
        print("💡 Make sure your .env file is configured")
        return

    # Run test
    tester = RealTimePriceTester()
    tester.test_all_pairs()

if __name__ == "__main__":
    main()