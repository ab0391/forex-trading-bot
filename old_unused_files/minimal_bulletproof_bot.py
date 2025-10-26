#!/usr/bin/env python3
"""
BULLETPROOF MINIMAL TRADING BOT
- Maximum 1 API call per run
- Runs every 2 hours (12 calls/day max)
- Simple, reliable, no complex caching
- Guaranteed under TwelveData limits
"""

import os
import time
import requests
import pandas as pd
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MinimalTradingBot:
    def __init__(self):
        self.api_key = os.getenv('TWELVEDATA_API_KEY', 'your_api_key_here')
        self.symbol = "EUR/USD"  # Single symbol only
        self.signals_file = "minimal_signals.json"
        
        logger.info("🚀 Minimal Bulletproof Bot Initialized")
        logger.info(f"📊 Tracking: {self.symbol}")
        logger.info(f"🔑 API Key: {'✅ Set' if self.api_key != 'your_api_key_here' else '❌ Missing'}")

    def get_price_data(self):
        """Get price data with SINGLE API call"""
        logger.info(f"📉 Making SINGLE API call for {self.symbol}")
        
        url = "https://api.twelvedata.com/time_series"
        params = {
            'symbol': self.symbol,
            'interval': '4h',
            'outputsize': 50,  # Minimal data
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'values' not in data:
                logger.error(f"❌ No data received: {data}")
                return None
                
            logger.info(f"✅ Received {len(data['values'])} data points")
            return data['values']
            
        except Exception as e:
            logger.error(f"❌ API call failed: {e}")
            return None

    def analyze_trend(self, data):
        """Simple trend analysis"""
        if not data or len(data) < 10:
            return "insufficient_data"
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['close'] = pd.to_numeric(df['close'])
        df = df.sort_values('datetime')
        
        # Simple moving averages
        df['sma_5'] = df['close'].rolling(5).mean()
        df['sma_10'] = df['close'].rolling(10).mean()
        
        current_price = df['close'].iloc[-1]
        sma_5 = df['sma_5'].iloc[-1]
        sma_10 = df['sma_10'].iloc[-1]
        
        logger.info(f"📊 Price: {current_price:.5f}")
        logger.info(f"📈 SMA5: {sma_5:.5f}, SMA10: {sma_10:.5f}")
        
        # Simple trend logic
        if sma_5 > sma_10 and current_price > sma_5:
            return "bullish"
        elif sma_5 < sma_10 and current_price < sma_5:
            return "bearish"
        else:
            return "neutral"

    def save_signal(self, trend, price):
        """Save signal to file"""
        signal = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'trend': trend,
            'price': price,
            'strategy': 'minimal_sma'
        }
        
        # Load existing signals
        signals = []
        if os.path.exists(self.signals_file):
            try:
                with open(self.signals_file, 'r') as f:
                    signals = json.load(f)
            except:
                signals = []
        
        # Add new signal
        signals.append(signal)
        
        # Keep only last 100 signals
        signals = signals[-100:]
        
        # Save back
        with open(self.signals_file, 'w') as f:
            json.dump(signals, f, indent=2)
            
        logger.info(f"💾 Signal saved: {trend}")

    def run_single_scan(self):
        """Run one complete scan - SINGLE API CALL ONLY"""
        logger.info("🎯 Starting minimal scan...")
        start_time = time.time()
        
        # Get data (1 API call)
        data = self.get_price_data()
        if not data:
            logger.error("❌ No data - scan failed")
            return False
            
        # Analyze trend
        trend = self.analyze_trend(data)
        current_price = float(data[0]['close'])
        
        # Save signal
        self.save_signal(trend, current_price)
        
        # Log results
        scan_time = time.time() - start_time
        logger.info(f"✅ Scan complete in {scan_time:.1f}s")
        logger.info(f"📊 Result: {self.symbol} = {trend.upper()} @ {current_price:.5f}")
        logger.info(f"🔥 API Calls Used: 1 (Guaranteed under limit)")
        
        return True

if __name__ == "__main__":
    bot = MinimalTradingBot()
    success = bot.run_single_scan()
    
    if success:
        logger.info("🎉 Minimal bot run successful!")
    else:
        logger.error("💥 Minimal bot run failed!")
        exit(1)
