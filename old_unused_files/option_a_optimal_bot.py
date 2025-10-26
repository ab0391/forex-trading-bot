#!/usr/bin/env python3
"""
OPTION A: OPTIMAL TRADING BOT
- 6 pairs per hour (single H4 timeframe)
- All 12 major pairs covered every 2 hours
- 6 API calls per hour (75% under 8/minute limit)
- Maximum trading opportunities while staying compliant
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

class OptimalTradingBot:
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
        
        # OPTION A SETTINGS: 6 pairs per hour
        self.pairs_per_hour = 6  # 6 pairs × 1 API call = 6 calls/hour
        self.signals_file = "optimal_signals.json"
        self.rotation_file = "optimal_rotation_state.json"
        
        logger.info("🚀 OPTION A: Optimal Trading Bot Initialized")
        logger.info(f"📊 Total Pairs: {len(self.all_pairs)}")
        logger.info(f"🔄 Pairs per Hour: {self.pairs_per_hour}")
        logger.info(f"⚡ API Calls per Hour: {self.pairs_per_hour} (75% under 8/min limit)")
        logger.info(f"🎯 Full Coverage: Every {len(self.all_pairs) // self.pairs_per_hour} hours")
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
            'total_pairs': len(self.all_pairs),
            'pairs_per_hour': self.pairs_per_hour
        }
        with open(self.rotation_file, 'w') as f:
            json.dump(state, f, indent=2)

    def get_current_pairs(self):
        """Get 6 pairs for current rotation"""
        start_index = self.get_rotation_state()
        
        # Get 6 pairs starting from current index
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
        logger.info(f"⏰ Next Cycle: {next_index // self.pairs_per_hour + 1}/{total_cycles}")
        
        return pairs

    def get_h4_data(self, symbol):
        """Get H4 data - SINGLE API CALL per pair"""
        url = "https://api.twelvedata.com/time_series"
        params = {
            'symbol': symbol,
            'interval': '4h',
            'outputsize': 200,  # More bars for comprehensive analysis
            'apikey': self.api_key
        }
        
        try:
            logger.info(f"📉 API CALL: {symbol} H4 (200 bars) - SINGLE CALL STRATEGY")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'values' not in data:
                logger.error(f"❌ No data for {symbol}: {data}")
                return None
                
            logger.info(f"✅ Received {len(data['values'])} H4 bars for {symbol}")
            return data['values']
            
        except Exception as e:
            logger.error(f"❌ API call failed for {symbol}: {e}")
            return None

    def calculate_enhanced_h4_analysis(self, df):
        """Enhanced H4 analysis with multiple indicators"""
        if len(df) < 50:
            return None
            
        # Multiple moving averages
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Support/Resistance zones
        highs = df['high'].rolling(window=10, center=True).max()
        lows = df['low'].rolling(window=10, center=True).min()
        
        resistance_levels = df[df['high'] == highs]['high'].dropna().tail(5)
        support_levels = df[df['low'] == lows]['low'].dropna().tail(5)
        
        return {
            'sma_20': df['sma_20'].iloc[-1],
            'sma_50': df['sma_50'].iloc[-1],
            'macd': df['macd'].iloc[-1],
            'macd_signal': df['macd_signal'].iloc[-1],
            'macd_histogram': df['macd_histogram'].iloc[-1],
            'rsi': df['rsi'].iloc[-1],
            'resistance_levels': resistance_levels.tolist(),
            'support_levels': support_levels.tolist()
        }

    def analyze_pair(self, symbol):
        """Analyze single pair with enhanced H4 strategy"""
        logger.info(f"🔍 Analyzing {symbol} (H4 Enhanced Strategy)...")
        
        # Get H4 data (SINGLE API CALL)
        h4_data = self.get_h4_data(symbol)
        
        if not h4_data:
            logger.warning(f"⚠️  No data for {symbol}")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(h4_data)
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')
        
        # Current price
        current_price = float(df['close'].iloc[-1])
        
        # Enhanced H4 analysis
        indicators = self.calculate_enhanced_h4_analysis(df)
        if not indicators:
            return None
        
        # Determine trend and signals
        trend = "neutral"
        signal_strength = "low"
        
        # Trend analysis
        if current_price > indicators['sma_20'] > indicators['sma_50']:
            trend = "bullish"
        elif current_price < indicators['sma_20'] < indicators['sma_50']:
            trend = "bearish"
        
        # Signal strength based on multiple factors
        strength_score = 0
        
        # MACD confirmation
        if indicators['macd'] > indicators['macd_signal'] and trend == "bullish":
            strength_score += 1
        elif indicators['macd'] < indicators['macd_signal'] and trend == "bearish":
            strength_score += 1
            
        # RSI confirmation
        if 30 < indicators['rsi'] < 70:  # Not overbought/oversold
            strength_score += 1
        elif indicators['rsi'] < 30 and trend == "bullish":  # Oversold + bullish
            strength_score += 2
        elif indicators['rsi'] > 70 and trend == "bearish":  # Overbought + bearish
            strength_score += 2
            
        # Zone proximity
        near_support = any(abs(current_price - level) / current_price * 10000 < 30 
                          for level in indicators['support_levels'])
        near_resistance = any(abs(current_price - level) / current_price * 10000 < 30 
                             for level in indicators['resistance_levels'])
        
        if near_support and trend == "bullish":
            strength_score += 2
        elif near_resistance and trend == "bearish":
            strength_score += 2
            
        # Determine signal strength
        if strength_score >= 4:
            signal_strength = "high"
        elif strength_score >= 2:
            signal_strength = "medium"
        else:
            signal_strength = "low"
        
        result = {
            'symbol': symbol,
            'current_price': current_price,
            'trend': trend,
            'signal_strength': signal_strength,
            'strength_score': strength_score,
            'rsi': round(indicators['rsi'], 2),
            'macd': round(indicators['macd'], 5),
            'near_support': near_support,
            'near_resistance': near_resistance,
            'support_levels': [round(x, 5) for x in indicators['support_levels']],
            'resistance_levels': [round(x, 5) for x in indicators['resistance_levels']]
        }
        
        # Log analysis
        zone_info = "Support" if near_support else "Resistance" if near_resistance else "None"
        logger.info(f"📊 {symbol}: {trend.upper()} @ {current_price:.5f} | Strength: {signal_strength.upper()} ({strength_score}/6) | Zone: {zone_info}")
        
        return result

    def save_signals(self, results):
        """Save analysis results"""
        signals = {
            'timestamp': datetime.now().isoformat(),
            'pairs_analyzed': len(results),
            'api_calls_used': len(results),  # 1 call per pair
            'strategy': 'H4_Enhanced_Single_Timeframe',
            'results': results
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
        
        # Keep only last 100 signal sets
        all_signals = all_signals[-100:]
        
        # Save back
        with open(self.signals_file, 'w') as f:
            json.dump(all_signals, f, indent=2)
            
        logger.info(f"💾 Signals saved for {len(results)} pairs")

    def run_optimal_scan(self):
        """Run optimal 6-pair scan with single H4 timeframe"""
        logger.info("🎯 Starting OPTION A: Optimal 6-Pair Scan...")
        start_time = time.time()
        
        # Get 6 pairs for this hour
        current_pairs = self.get_current_pairs()
        
        # Analyze each pair (1 API call each)
        results = []
        api_calls = 0
        
        for i, symbol in enumerate(current_pairs, 1):
            logger.info(f"📈 Processing {symbol} ({i}/{len(current_pairs)})...")
            result = self.analyze_pair(symbol)
            if result:
                results.append(result)
            api_calls += 1
            
            # Extended delay between pairs to ensure 8/minute compliance
            if i < len(current_pairs):
                time.sleep(12)  # 12-second delay = 5 calls/minute max
        
        # Save results
        if results:
            self.save_signals(results)
        
        # Log summary
        scan_time = time.time() - start_time
        high_signals = [r for r in results if r['signal_strength'] == 'high']
        medium_signals = [r for r in results if r['signal_strength'] == 'medium']
        
        logger.info(f"✅ OPTION A Scan Complete in {scan_time:.1f}s")
        logger.info(f"📊 Pairs Analyzed: {len(results)}")
        logger.info(f"🔥 API Calls Used: {api_calls}/6 (75% under 8/min limit)")
        logger.info(f"🎯 High Signals: {len(high_signals)} | Medium: {len(medium_signals)}")
        logger.info(f"⏰ Next Full Coverage: {2 - ((api_calls // 6) % 2)} hours")
        
        # Log high-quality signals
        for signal in high_signals:
            zone = "near Support" if signal['near_support'] else "near Resistance" if signal['near_resistance'] else ""
            logger.info(f"🚨 HIGH SIGNAL: {signal['symbol']} {signal['trend'].upper()} @ {signal['current_price']:.5f} {zone}")
        
        return len(results) > 0

if __name__ == "__main__":
    bot = OptimalTradingBot()
    success = bot.run_optimal_scan()
    
    if success:
        logger.info("🎉 Option A optimal scan successful!")
    else:
        logger.error("💥 Option A optimal scan failed!")
        exit(1)
