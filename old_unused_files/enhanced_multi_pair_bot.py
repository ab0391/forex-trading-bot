#!/usr/bin/env python3
"""
ENHANCED MULTI-PAIR TRADING BOT
- All 8 major pairs + 4 popular crosses = 12 pairs total
- Smart rotation: 4 pairs per hour (3 API calls each = 12 calls/hour)
- Runs every hour for better entry timing
- Uses original zone detection strategy
- Stays under API limits: 12 calls/hour vs 800/day limit
"""

import os
import time
import requests
import pandas as pd
import logging
from datetime import datetime
import json
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedMultiPairBot:
    def __init__(self):
        self.api_key = os.getenv('TWELVEDATA_API_KEY', 'your_api_key_here')
        
        # ALL MAJOR PAIRS + POPULAR CROSSES (12 total)
        self.all_pairs = [
            # Major USD pairs (8)
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
            "USD/CHF", "NZD/USD", "USD/CAD", "USD/SEK",
            # Popular crosses (4)  
            "EUR/GBP", "GBP/JPY", "EUR/JPY", "AUD/JPY"
        ]
        
        # Rotation settings
        self.pairs_per_hour = 4  # 4 pairs × 3 API calls = 12 calls/hour
        self.signals_file = "enhanced_signals.json"
        self.rotation_file = "rotation_state.json"
        
        logger.info("🚀 Enhanced Multi-Pair Bot Initialized")
        logger.info(f"📊 Total Pairs: {len(self.all_pairs)}")
        logger.info(f"🔄 Pairs per Hour: {self.pairs_per_hour}")
        logger.info(f"🔑 API Key: {'✅ Set' if self.api_key != 'your_api_key_here' else '❌ Missing'}")

    def get_rotation_state(self):
        """Get current rotation position"""
        try:
            if os.path.exists(self.rotation_file):
                with open(self.rotation_file, 'r') as f:
                    state = json.load(f)
                    return state.get('current_index', 0)
        except:
            pass
        return 0

    def save_rotation_state(self, index):
        """Save rotation position"""
        state = {
            'current_index': index,
            'timestamp': datetime.now().isoformat(),
            'total_pairs': len(self.all_pairs)
        }
        with open(self.rotation_file, 'w') as f:
            json.dump(state, f, indent=2)

    def get_current_pairs(self):
        """Get pairs for current rotation"""
        start_index = self.get_rotation_state()
        
        # Get 4 pairs starting from current index
        pairs = []
        for i in range(self.pairs_per_hour):
            pair_index = (start_index + i) % len(self.all_pairs)
            pairs.append(self.all_pairs[pair_index])
        
        # Update rotation for next hour
        next_index = (start_index + self.pairs_per_hour) % len(self.all_pairs)
        self.save_rotation_state(next_index)
        
        # Log rotation info
        cycle_position = (start_index // self.pairs_per_hour) + 1
        total_cycles = len(self.all_pairs) // self.pairs_per_hour
        
        logger.info(f"🎯 Rotation Cycle {cycle_position}/{total_cycles}")
        logger.info(f"📈 Current Pairs: {', '.join(pairs)}")
        
        return pairs

    def get_timeframe_data(self, symbol, timeframe, bars=100):
        """Get data for specific timeframe"""
        url = "https://api.twelvedata.com/time_series"
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'outputsize': bars,
            'apikey': self.api_key
        }
        
        try:
            logger.info(f"📉 API CALL: {symbol} {timeframe} ({bars} bars)")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'values' not in data:
                logger.error(f"❌ No data for {symbol} {timeframe}: {data}")
                return None
                
            return data['values']
            
        except Exception as e:
            logger.error(f"❌ API call failed for {symbol} {timeframe}: {e}")
            return None

    def calculate_zones(self, df):
        """Calculate support/resistance zones (simplified version)"""
        if len(df) < 20:
            return []
            
        # Find swing highs and lows
        highs = df['high'].rolling(window=5, center=True).max()
        lows = df['low'].rolling(window=5, center=True).min()
        
        swing_highs = df[df['high'] == highs]['high'].dropna()
        swing_lows = df[df['low'] == lows]['low'].dropna()
        
        # Combine and sort zones
        zones = []
        for high in swing_highs.tail(5):  # Last 5 resistance zones
            zones.append({'level': high, 'type': 'resistance'})
        for low in swing_lows.tail(5):   # Last 5 support zones
            zones.append({'level': low, 'type': 'support'})
            
        return zones

    def analyze_pair(self, symbol):
        """Analyze single pair with multi-timeframe approach"""
        logger.info(f"🔍 Analyzing {symbol}...")
        
        # Get multi-timeframe data (3 API calls per pair)
        d1_data = self.get_timeframe_data(symbol, '1day', 50)
        h4_data = self.get_timeframe_data(symbol, '4h', 100)
        h1_data = self.get_timeframe_data(symbol, '1h', 100)
        
        if not all([d1_data, h4_data, h1_data]):
            logger.warning(f"⚠️  Insufficient data for {symbol}")
            return None
            
        # Convert to DataFrames
        d1_df = pd.DataFrame(d1_data)
        h4_df = pd.DataFrame(h4_data)
        h1_df = pd.DataFrame(h1_data)
        
        for df in [d1_df, h4_df, h1_df]:
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime')
        
        # Current price
        current_price = float(h1_df['close'].iloc[-1])
        
        # Calculate zones and bias
        d1_zones = self.calculate_zones(d1_df)
        h4_zones = self.calculate_zones(h4_df)
        
        # Simple bias calculation
        d1_sma = d1_df['close'].rolling(10).mean().iloc[-1]
        h4_sma = h4_df['close'].rolling(20).mean().iloc[-1]
        
        # Determine bias
        if current_price > d1_sma and current_price > h4_sma:
            bias = "bullish"
        elif current_price < d1_sma and current_price < h4_sma:
            bias = "bearish"
        else:
            bias = "neutral"
            
        # Check for zone proximity (simplified)
        near_zone = False
        zone_type = None
        for zone in h4_zones[-3:]:  # Check last 3 zones
            distance = abs(current_price - zone['level']) / current_price * 10000  # pips
            if distance < 20:  # Within 20 pips
                near_zone = True
                zone_type = zone['type']
                break
        
        result = {
            'symbol': symbol,
            'current_price': current_price,
            'bias': bias,
            'near_zone': near_zone,
            'zone_type': zone_type,
            'd1_zones': len(d1_zones),
            'h4_zones': len(h4_zones),
            'signal_strength': 'high' if near_zone and bias != 'neutral' else 'medium' if bias != 'neutral' else 'low'
        }
        
        logger.info(f"📊 {symbol}: {bias.upper()} @ {current_price:.5f} | Zone: {zone_type if near_zone else 'None'}")
        return result

    def save_signals(self, results):
        """Save analysis results"""
        signals = {
            'timestamp': datetime.now().isoformat(),
            'pairs_analyzed': len(results),
            'results': results,
            'api_calls_used': len(results) * 3
        }
        
        # Load existing signals
        all_signals = []
        if os.path.exists(self.signals_file):
            try:
                with open(self.signals_file, 'r') as f:
                    all_signals = json.load(f)
            except:
                all_signals = []
        
        # Add new signals
        all_signals.append(signals)
        
        # Keep only last 50 signal sets
        all_signals = all_signals[-50:]
        
        # Save back
        with open(self.signals_file, 'w') as f:
            json.dump(all_signals, f, indent=2)
            
        logger.info(f"💾 Signals saved for {len(results)} pairs")

    def run_hourly_scan(self):
        """Run complete hourly scan"""
        logger.info("🎯 Starting Enhanced Multi-Pair Scan...")
        start_time = time.time()
        
        # Get pairs for this hour
        current_pairs = self.get_current_pairs()
        
        # Analyze each pair
        results = []
        api_calls = 0
        
        for symbol in current_pairs:
            result = self.analyze_pair(symbol)
            if result:
                results.append(result)
            api_calls += 3  # 3 calls per pair
            
            # Small delay between pairs
            time.sleep(2)
        
        # Save results
        if results:
            self.save_signals(results)
        
        # Log summary
        scan_time = time.time() - start_time
        high_signals = [r for r in results if r['signal_strength'] == 'high']
        
        logger.info(f"✅ Scan complete in {scan_time:.1f}s")
        logger.info(f"📊 Pairs Analyzed: {len(results)}")
        logger.info(f"🔥 API Calls Used: {api_calls} (well under 800/day limit)")
        logger.info(f"🎯 High-Quality Signals: {len(high_signals)}")
        
        # Log high-quality signals
        for signal in high_signals:
            logger.info(f"🚨 SIGNAL: {signal['symbol']} {signal['bias'].upper()} @ {signal['current_price']:.5f} near {signal['zone_type']}")
        
        return len(results) > 0

if __name__ == "__main__":
    bot = EnhancedMultiPairBot()
    success = bot.run_hourly_scan()
    
    if success:
        logger.info("🎉 Enhanced multi-pair scan successful!")
    else:
        logger.error("💥 Enhanced multi-pair scan failed!")
        exit(1)
