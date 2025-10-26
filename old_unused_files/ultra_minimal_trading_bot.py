#!/usr/bin/env python3
"""
Ultra-Minimal Trading Bot - MAXIMUM API Credit Savings
- Single symbol: EUR/USD only
- Single timeframe: 1d only
- 1 API call per scan maximum
- Target: 48 calls/day = 6% of 800 limit
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ULTRA_MINIMAL - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltraMinimalBot:
    def __init__(self):
        # ABSOLUTE MINIMUM: Only EUR/USD daily
        self.symbol = "EUR/USD"
        self.timeframe = "1d"

        # API credentials
        self.api_key = os.getenv("TWELVEDATA_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        logger.info("🚀 Ultra-Minimal Bot initialized")
        logger.info(f"📊 Tracking: {self.symbol} {self.timeframe} ONLY")
        logger.info("⚡ Target: 1 API call per scan, 48/day = 6% limit usage")

    def fetch_minimal_data(self):
        """Fetch minimal data - EXACTLY 1 API call"""
        try:
            logger.info("📞 Making SINGLE API call for EUR/USD daily data...")

            url = "https://api.twelvedata.com/time_series"
            params = {
                "symbol": self.symbol,
                "interval": self.timeframe,
                "outputsize": "50",  # Minimal but sufficient for analysis
                "apikey": self.api_key
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if "values" in data and len(data["values"]) >= 20:
                    # Convert to DataFrame
                    df = pd.DataFrame(data["values"])
                    df.columns = ["datetime", "open", "high", "low", "close", "volume"]

                    # Convert to numeric
                    for col in ["open", "high", "low", "close"]:
                        df[col] = pd.to_numeric(df[col])

                    df = df.sort_values("datetime").reset_index(drop=True)

                    logger.info(f"✅ Data received: {len(df)} daily bars for {self.symbol}")
                    logger.info("💳 Used exactly 1 API credit")

                    return df
                else:
                    logger.error(f"❌ Invalid data structure: {data}")
                    return None
            else:
                logger.error(f"❌ API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Data fetch failed: {e}")
            return None

    def analyze_minimal_setup(self, df):
        """Ultra-simple analysis with minimal data"""
        try:
            if len(df) < 20:
                logger.warning("⚠️ Insufficient data for analysis")
                return None

            # Get recent prices
            close = df["close"]
            current_price = close.iloc[-1]
            previous_price = close.iloc[-2]

            # Simple moving averages
            sma_20 = close.rolling(20).mean().iloc[-1]
            sma_10 = close.rolling(10).mean().iloc[-1]

            # Price change
            daily_change = current_price - previous_price
            daily_change_pct = (daily_change / previous_price) * 100

            # Simple trend determination
            trend = "BULLISH" if current_price > sma_20 and sma_10 > sma_20 else "BEARISH"

            # Signal strength
            if abs(daily_change_pct) > 0.5:  # Significant daily move
                signal_strength = "STRONG"
            elif abs(daily_change_pct) > 0.2:
                signal_strength = "MEDIUM"
            else:
                signal_strength = "WEAK"

            analysis = {
                "symbol": self.symbol,
                "current_price": current_price,
                "daily_change": daily_change,
                "daily_change_pct": daily_change_pct,
                "sma_20": sma_20,
                "sma_10": sma_10,
                "trend": trend,
                "signal_strength": signal_strength
            }

            logger.info(f"📈 Analysis: {trend} trend, {signal_strength} signal ({daily_change_pct:+.2f}%)")

            return analysis

        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return None

    def send_minimal_alert(self, analysis):
        """Send alert only for significant moves"""
        try:
            if not analysis:
                return False

            # Only send alerts for medium/strong signals
            if analysis["signal_strength"] == "WEAK":
                logger.info("📊 Weak signal - no alert sent")
                return False

            # Determine emoji based on trend
            trend_emoji = "🟢" if analysis["trend"] == "BULLISH" else "🔴"
            strength_emoji = "🚨" if analysis["signal_strength"] == "STRONG" else "⚠️"

            message = f"""{strength_emoji} <b>EUR/USD Ultra-Minimal Alert</b>

{trend_emoji} <b>Trend:</b> {analysis['trend']}
💰 <b>Price:</b> {analysis['current_price']:.5f}
📊 <b>Daily Change:</b> {analysis['daily_change_pct']:+.2f}%
📈 <b>Signal:</b> {analysis['signal_strength']}

🔢 <b>Technical:</b>
• SMA 20: {analysis['sma_20']:.5f}
• SMA 10: {analysis['sma_10']:.5f}

⚡ <b>API Usage:</b> 1 credit used
📊 <b>Daily Target:</b> 48/800 credits (6%)"""

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                logger.info("✅ Alert sent successfully")
                return True
            else:
                logger.error(f"❌ Telegram error: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Alert failed: {e}")
            return False

    def run_ultra_minimal_scan(self):
        """Run complete scan with exactly 1 API call"""
        start_time = datetime.now()

        logger.info("🤖 Starting Ultra-Minimal Scan...")
        logger.info("=" * 50)

        try:
            # Step 1: Fetch data (1 API call)
            df = self.fetch_minimal_data()

            if df is not None:
                # Step 2: Analyze data (no API calls)
                analysis = self.analyze_minimal_setup(df)

                if analysis:
                    # Step 3: Send alert if significant (no API calls)
                    alert_sent = self.send_minimal_alert(analysis)

                    if alert_sent:
                        logger.info("📱 Alert sent for significant move")
                    else:
                        logger.info("📊 No alert needed (weak signal)")
                else:
                    logger.warning("⚠️ Analysis failed")
            else:
                logger.error("❌ Data fetch failed")

            # Summary
            duration = (datetime.now() - start_time).total_seconds()
            logger.info("=" * 50)
            logger.info(f"✅ Ultra-minimal scan complete in {duration:.1f}s")
            logger.info("💳 Used exactly 1 API credit")
            logger.info("📊 Daily usage: 48 scans × 1 credit = 48/800 (6%)")

        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")

if __name__ == "__main__":
    print("🚀 Ultra-Minimal Trading Bot")
    print("💡 Maximum API credit savings mode")
    print("📊 EUR/USD Daily analysis only - 1 API call per scan")
    print("⚡ Target: 48 calls/day = 6% of 800 credit limit")
    print("=" * 60)

    bot = UltraMinimalBot()
    bot.run_ultra_minimal_scan()