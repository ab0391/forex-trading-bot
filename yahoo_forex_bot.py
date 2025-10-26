#!/usr/bin/env python3
"""
Yahoo Finance Trading Bot - NO RATE LIMITS!
- All major forex pairs + gold + commodities + crypto
- Works with dashboard and Telegram
- Completely free with no API restrictions
"""

import os
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Yahoo Finance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    logger.info("✅ Yahoo Finance loaded - NO RATE LIMITS!")
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.error("❌ yfinance not installed. Install with: pip install yfinance")

# Import Trade Tracker
try:
    from trade_tracker import TradeTracker
    TRADE_TRACKER_AVAILABLE = True
    logger.info("✅ Trade Tracker loaded - Signal deduplication enabled!")
except ImportError:
    TRADE_TRACKER_AVAILABLE = False
    logger.error("❌ Trade Tracker not available")

# Import Dynamic R:R Optimizer
try:
    from dynamic_rr_optimizer import DynamicRROptimizer
    DYNAMIC_RR_AVAILABLE = True
    logger.info("✅ Dynamic R:R Optimizer loaded - AI-powered R:R (2:1 to 5:1)!")
except ImportError:
    DYNAMIC_RR_AVAILABLE = False
    logger.error("❌ Dynamic R:R Optimizer not available")

class TelegramNotifier:
    """Telegram notifications for trading signals"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    def send_message(self, message, parse_mode="Markdown"):
        """Send basic message to Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured")
            return False
            
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("✅ Telegram message sent")
            return True
        except Exception as e:
            logger.error(f"❌ Telegram message failed: {e}")
            return False
        
    def send_trading_alert(self, symbol, zone_type, entry, stop, target, rr, bias_info, current_price):
        """Send trading alert to Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured")
            return False
            
        message = f"""
🚨 **TRADING SIGNAL ALERT**

📊 **Pair:** {symbol}
📈 **Type:** {zone_type.upper()} Zone Entry
💰 **Entry:** {entry:.5f}
🛑 **Stop Loss:** {stop:.5f}
🎯 **Take Profit:** {target:.5f}
📐 **Risk/Reward:** {rr:.1f}:1

📋 **Analysis:**
{bias_info}

💵 **Current Price:** {current_price:.5f}
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 **Bot:** Yahoo Finance Enhanced (FREE)
"""
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Telegram alert sent for {symbol}")
            return True
        except Exception as e:
            logger.error(f"❌ Telegram alert failed: {e}")
            return False

class YahooDataFetcher:
    """Fetch data from Yahoo Finance - NO RATE LIMITS!"""
    
    def __init__(self):
        self.symbol_mapping = {
            # Forex pairs
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X", 
            "USD/JPY": "USDJPY=X",
            "AUD/USD": "AUDUSD=X",
            "USD/CHF": "USDCHF=X",
            "NZD/USD": "NZDUSD=X",
            "USD/CAD": "USDCAD=X",
            "EUR/GBP": "EURGBP=X",
            "EUR/JPY": "EURJPY=X",
            "GBP/JPY": "GBPJPY=X",
            "AUD/JPY": "AUDJPY=X",
            "EUR/CHF": "EURCHF=X",
            "GBP/CHF": "GBPCHF=X",
            "AUD/CAD": "AUDCAD=X",
            
            # Commodities
            "GOLD": "GC=F",
            "SILVER": "SI=F", 
            "OIL": "CL=F",
            
            # Crypto
            "BITCOIN": "BTC-USD",
            "ETHEREUM": "ETH-USD"
        }
    
    def get_current_price(self, symbol):
        """Get current price from Yahoo Finance"""
        try:
            yahoo_symbol = self.symbol_mapping.get(symbol, f"{symbol.replace('/', '')}=X")
            ticker = yf.Ticker(yahoo_symbol)
            
            # Try multiple methods to get price
            info = ticker.info
            if 'regularMarketPrice' in info:
                price = info['regularMarketPrice']
            elif 'currentPrice' in info:
                price = info['currentPrice']
            elif 'ask' in info:
                price = info['ask']
            else:
                # Fallback to fast_info
                fast_info = ticker.fast_info
                price = fast_info.get('lastPrice', None)
            
            if price:
                logger.info(f"✅ Yahoo Finance: {symbol} = {price:.5f} (FREE)")
                return float(price)
            else:
                logger.warning(f"⚠️  No price data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Yahoo Finance error for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol, period="1mo"):
        """Get historical data for analysis"""
        try:
            yahoo_symbol = self.symbol_mapping.get(symbol, f"{symbol.replace('/', '')}=X")
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get historical data
            hist = ticker.history(period=period, interval="1h")
            
            if not hist.empty:
                logger.info(f"✅ Historical data: {symbol} ({len(hist)} candles)")
                return hist
            else:
                logger.warning(f"⚠️  No historical data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Historical data error for {symbol}: {e}")
            return None

class MarketHoursChecker:
    """Check if markets are open for trading"""
    
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')
        self.london_tz = pytz.timezone('Europe/London')
        self.tokyo_tz = pytz.timezone('Asia/Tokyo')
        self.sydney_tz = pytz.timezone('Australia/Sydney')
    
    def is_forex_market_open(self):
        """Check if forex markets are open (24/5 but with reduced activity on weekends)"""
        now = datetime.now(pytz.UTC)
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Forex markets are closed on weekends (Saturday=5, Sunday=6)
        if weekday >= 5:  # Saturday or Sunday
            return False, "Weekend - Forex markets closed"
        
        # Check if it's during major session overlaps for better liquidity
        ny_time = now.astimezone(self.ny_tz)
        london_time = now.astimezone(self.london_tz)
        tokyo_time = now.astimezone(self.tokyo_tz)
        
        # Major session times (in local time)
        ny_open = ny_time.replace(hour=8, minute=0, second=0, microsecond=0)
        ny_close = ny_time.replace(hour=17, minute=0, second=0, microsecond=0)
        
        london_open = london_time.replace(hour=8, minute=0, second=0, microsecond=0)
        london_close = london_time.replace(hour=16, minute=30, second=0, microsecond=0)
        
        tokyo_open = tokyo_time.replace(hour=9, minute=0, second=0, microsecond=0)
        tokyo_close = tokyo_time.replace(hour=15, minute=0, second=0, microsecond=0)
        
        # Check if any major session is open
        ny_active = ny_open <= ny_time <= ny_close
        london_active = london_open <= london_time <= london_close
        tokyo_active = tokyo_open <= tokyo_time <= tokyo_close
        
        if ny_active or london_active or tokyo_active:
            active_sessions = []
            if ny_active: active_sessions.append("NY")
            if london_active: active_sessions.append("London")
            if tokyo_active: active_sessions.append("Tokyo")
            return True, f"Markets open - Active sessions: {', '.join(active_sessions)}"
        
        return False, "Outside major trading sessions"
    
    def is_crypto_market_open(self):
        """Crypto markets are 24/7"""
        return True, "Crypto markets open 24/7"
    
    def is_commodity_market_open(self):
        """Check if commodity markets are open"""
        now = datetime.now(pytz.UTC)
        weekday = now.weekday()
        
        # Commodity markets closed on weekends
        if weekday >= 5:
            return False, "Weekend - Commodity markets closed"
        
        # NY Mercantile Exchange hours (approximate)
        ny_time = now.astimezone(self.ny_tz)
        open_time = ny_time.replace(hour=6, minute=0, second=0, microsecond=0)
        close_time = ny_time.replace(hour=17, minute=0, second=0, microsecond=0)
        
        if open_time <= ny_time <= close_time:
            return True, "Commodity markets open (NYMEX hours)"
        
        return False, "Commodity markets closed (outside NYMEX hours)"
    
    def should_trade_symbol(self, symbol):
        """Determine if we should trade a specific symbol based on market hours"""
        if symbol in ["BITCOIN", "ETHEREUM"]:
            return self.is_crypto_market_open()
        elif symbol in ["GOLD", "SILVER", "OIL"]:
            return self.is_commodity_market_open()
        else:  # Forex pairs
            return self.is_forex_market_open()

class ZoneDetector:
    """Detect support/resistance zones"""
    
    def find_zones(self, df):
        """Find support and resistance zones - IMPROVED VERSION"""
        if df is None or df.empty:
            return []
        
        # Use a more robust zone detection method
        # Look for significant price levels that have been tested multiple times
        
        # Find pivot highs and lows with larger window for better accuracy
        df['pivot_high'] = df['High'].rolling(window=5, center=True).max() == df['High']
        df['pivot_low'] = df['Low'].rolling(window=5, center=True).min() == df['Low']
        
        # Get significant levels (more than 1 touch)
        resistance_levels = []
        support_levels = []
        
        # Find resistance zones (supply) - look for levels that were tested multiple times
        for idx, row in df.iterrows():
            if row['pivot_high']:
                level = row['High']
                # Count how many times this level was tested (within 0.2% tolerance)
                tolerance = level * 0.002  # 0.2% tolerance (more flexible)
                touches = len(df[(df['High'] >= level - tolerance) & (df['High'] <= level + tolerance)])
                if touches >= 1:  # At least 1 touch for significance (more sensitive)
                    resistance_levels.append({
                        'type': 'supply',
                        'price': level,
                        'strength': touches,
                        'touches': touches
                    })
        
        # Find support zones (demand) - look for levels that were tested multiple times
        for idx, row in df.iterrows():
            if row['pivot_low']:
                level = row['Low']
                # Count how many times this level was tested (within 0.2% tolerance)
                tolerance = level * 0.002  # 0.2% tolerance (more flexible)
                touches = len(df[(df['Low'] >= level - tolerance) & (df['Low'] <= level + tolerance)])
                if touches >= 1:  # At least 1 touch for significance (more sensitive)
                    support_levels.append({
                        'type': 'demand',
                        'price': level,
                        'strength': touches,
                        'touches': touches
                    })
        
        # Combine and sort by strength (number of touches)
        all_zones = resistance_levels + support_levels
        all_zones.sort(key=lambda x: x['strength'], reverse=True)
        
        # Remove duplicate zones (within 0.1% of each other)
        filtered_zones = []
        for zone in all_zones:
            is_duplicate = False
            for existing_zone in filtered_zones:
                if abs(zone['price'] - existing_zone['price']) / existing_zone['price'] < 0.001:
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered_zones.append(zone)
        
        return filtered_zones[:10]  # Return top 10 strongest zones

class YahooTradingBot:
    """Main trading bot using Yahoo Finance"""
    
    def __init__(self):
        self.data_fetcher = YahooDataFetcher()
        self.zone_detector = ZoneDetector()
        self.notifier = TelegramNotifier()
        self.market_checker = MarketHoursChecker()
        
        # Initialize trade tracker for signal deduplication
        if TRADE_TRACKER_AVAILABLE:
            self.trade_tracker = TradeTracker()
            logger.info("✅ Trade Tracker initialized - Preventing contradictory signals")
        else:
            self.trade_tracker = None
            logger.warning("⚠️ Trade Tracker not available - Signals may be contradictory")
        
        # Initialize dynamic R:R optimizer
        if DYNAMIC_RR_AVAILABLE:
            self.rr_optimizer = DynamicRROptimizer()
            logger.info("✅ Dynamic R:R Optimizer initialized - AI-powered optimization (2:1 to 5:1)")
        else:
            self.rr_optimizer = None
            logger.warning("⚠️ Dynamic R:R not available - Using fixed 2:1 ratio")
        
        # EXPANDED PAIRS LIST - NO RATE LIMITS!
        self.all_symbols = [
            # Major Forex Pairs
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
            "USD/CHF", "NZD/USD", "USD/CAD", "EUR/GBP",
            
            # Popular Cross Pairs (EUR crosses)
            "EUR/JPY", "EUR/CHF", "EUR/AUD", "EUR/NZD", "EUR/CAD",
            
            # Popular Cross Pairs (GBP crosses)
            "GBP/JPY", "GBP/CHF", "GBP/AUD", "GBP/NZD", "GBP/CAD",
            
            # Popular Cross Pairs (Other)
            "AUD/JPY", "AUD/CAD", "AUD/NZD",
            "NZD/JPY", "CAD/JPY", "CHF/JPY",
            
            # Commodities
            "GOLD", "SILVER", "OIL",
            
            # Crypto
            "BITCOIN", "ETHEREUM"
        ]
        
        # Rotation settings
        self.symbols_per_cycle = 10  # Doubled for faster rotation - NO RATE LIMITS!
        self.scan_count = 0
        self.signals_file = Path("signals_history.json")
        
        logger.info(f"🚀 Yahoo Finance Trading Bot Initialized")
        logger.info(f"📊 Trading Pairs: {len(self.all_symbols)} (NO RATE LIMITS!)")
        logger.info(f"🔄 Pairs per Cycle: {self.symbols_per_cycle}")
        logger.info(f"💰 Cost: $0/month (100% FREE)")
        logger.info(f"⚡ Rate Limits: NONE")
        
    def get_symbols_for_current_scan(self):
        """Get symbols for current scan"""
        start_idx = (self.scan_count * self.symbols_per_cycle) % len(self.all_symbols)
        end_idx = start_idx + self.symbols_per_cycle
        
        if end_idx > len(self.all_symbols):
            symbols = self.all_symbols[start_idx:] + self.all_symbols[:end_idx - len(self.all_symbols)]
        else:
            symbols = self.all_symbols[start_idx:end_idx]
            
        self.scan_count += 1
        return symbols
    
    def analyze_symbol(self, symbol):
        """Analyze a single symbol for trading opportunities"""
        logger.info(f"🔍 Analyzing {symbol}...")
        
        # Check if we can generate a signal for this symbol (trade tracking)
        if self.trade_tracker and not self.trade_tracker.can_generate_signal(symbol):
            return None
        
        # Check if markets are open for this symbol
        market_open, market_status = self.market_checker.should_trade_symbol(symbol)
        if not market_open:
            logger.info(f"⏰ Markets closed for {symbol}: {market_status}")
            return None
        
        # Get current price
        current_price = self.data_fetcher.get_current_price(symbol)
        if not current_price:
            return None
        
        # Get historical data
        hist_data = self.data_fetcher.get_historical_data(symbol)
        if hist_data is None:
            return None
        
        # Find zones
        zones = self.zone_detector.find_zones(hist_data)
        
        # Log zone detection for debugging
        if zones:
            demand_zones = [z for z in zones if z['type'] == 'demand']
            supply_zones = [z for z in zones if z['type'] == 'supply']
            logger.info(f"🔍 {symbol}: Found {len(demand_zones)} demand zones, {len(supply_zones)} supply zones")
        
        # Look for trading opportunities
        for zone in zones:
            zone_price = zone['price']
            zone_type = zone['type']
            
            # Check if price is near zone
            distance = abs(current_price - zone_price) / current_price
            
            if distance < 0.005:  # Within 0.5%
                # Calculate entry
                entry = current_price
                
                # Use Dynamic R:R Optimizer if available
                if self.rr_optimizer:
                    # AI-powered R:R optimization (2:1 to 5:1)
                    optimal_rr, confidence, rr_explanation = self.rr_optimizer.optimize_rr_ratio(
                        hist_data, current_price, zone_price, zone_type
                    )
                    
                    # Calculate stop and target based on optimized R:R
                    stop, target = self.rr_optimizer.calculate_stop_and_target(
                        entry, zone_type, optimal_rr
                    )
                    
                    risk_reward = optimal_rr
                    bias_info = f"Price near {zone_type} zone. {'LONG' if zone_type == 'demand' else 'SHORT'} signal with {risk_reward:.1f}:1 R:R (AI-optimized: {rr_explanation})"
                    
                else:
                    # Fallback to fixed 2:1 R:R if optimizer not available
                    if zone_type == 'demand':
                        # For demand zones (support), we go LONG
                        stop = entry * 0.995  # 0.5% below entry for stop loss
                        target = entry * 1.010  # 1.0% above entry for take profit (2:1 R:R)
                    else:  # supply
                        # For supply zones (resistance), we go SHORT
                        stop = entry * 1.005  # 0.5% above entry for stop loss
                        target = entry * 0.990  # 1.0% below entry for take profit (2:1 R:R)
                    
                    # Calculate risk/reward ratio properly
                    risk = abs(entry - stop)
                    reward = abs(target - entry)
                    
                    if risk > 0:
                        risk_reward = reward / risk
                    else:
                        risk_reward = 0
                    
                    bias_info = f"Price near {zone_type} zone. {'LONG' if zone_type == 'demand' else 'SHORT'} signal with {risk_reward:.1f}:1 R:R"
                
                if risk_reward >= 2.0:  # Minimum 2:1 R:R
                    signal = {
                        'signal_id': f"{symbol}_{zone_type}_{int(time.time())}",
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'zone_type': zone_type,
                        'entry': entry,
                        'stop': stop,
                        'target': target,
                        'risk_reward': risk_reward,
                        'current_price': current_price,
                        'bias_info': bias_info,
                        'status': 'active'
                    }
                    
                    # Add to trade tracker to prevent contradictory signals
                    if self.trade_tracker:
                        self.trade_tracker.add_active_trade(signal)
                        logger.info(f"📊 Added {symbol} to active trades - No contradictory signals allowed")
                    
                    return signal
        
        return None
    
    def save_signal(self, signal):
        """Save signal to file for dashboard"""
        try:
            signals = []
            if self.signals_file.exists():
                with open(self.signals_file, 'r') as f:
                    signals = json.load(f)
            
            signals.append(signal)
            
            # Keep only last 100 signals
            if len(signals) > 100:
                signals = signals[-100:]
            
            with open(self.signals_file, 'w') as f:
                json.dump(signals, f, indent=2)
                
            logger.info(f"💾 Signal saved: {signal['signal_id']}")
            
        except Exception as e:
            logger.error(f"❌ Error saving signal: {e}")
    
    def run_scan_cycle(self):
        """Run one complete scan cycle"""
        logger.info(f"🔄 Starting scan cycle {self.scan_count + 1}")
        
        symbols = self.get_symbols_for_current_scan()
        signals_found = 0
        
        for symbol in symbols:
            try:
                signal = self.analyze_symbol(symbol)
                if signal:
                    # Save to dashboard
                    self.save_signal(signal)
                    
                    # Send Telegram alert
                    self.notifier.send_trading_alert(
                        symbol=signal['symbol'],
                        zone_type=signal['zone_type'],
                        entry=signal['entry'],
                        stop=signal['stop'],
                        target=signal['target'],
                        rr=signal['risk_reward'],
                        bias_info=signal['bias_info'],
                        current_price=signal['current_price']
                    )
                    
                    signals_found += 1
                    logger.info(f"🎯 Signal found: {symbol}")
                
                # Small delay between symbols
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {symbol}: {e}")
        
        logger.info(f"✅ Scan complete: {signals_found} signals found")
        return signals_found

def main():
    """Main trading loop"""
    if not YFINANCE_AVAILABLE:
        print("❌ Yahoo Finance not available. Install with: pip install yfinance")
        return
    
    bot = YahooTradingBot()
    
    print("🚀 Yahoo Finance Trading Bot Started!")
    print("💰 Cost: $0/month (100% FREE)")
    print("⚡ Rate Limits: NONE")
    print("📊 Pairs: 19 (Forex + Gold + Crypto)")
    print("📱 Telegram: Enabled")
    print("🖥️  Dashboard: Enabled")
    print("🕐 Market Hours: Smart detection enabled")
    print("\nPress Ctrl+C to stop...")
    
    try:
        while True:
            # Check market status before scanning
            forex_open, forex_status = bot.market_checker.is_forex_market_open()
            crypto_open, crypto_status = bot.market_checker.is_crypto_market_open()
            commodity_open, commodity_status = bot.market_checker.is_commodity_market_open()
            
            logger.info(f"🕐 Market Status:")
            logger.info(f"   Forex: {forex_status}")
            logger.info(f"   Crypto: {crypto_status}")
            logger.info(f"   Commodities: {commodity_status}")
            
            if not (forex_open or crypto_open or commodity_open):
                logger.info("⏰ All markets closed - waiting 1 hour before next check...")
                time.sleep(60 * 60)  # Wait 1 hour when markets are closed
                continue
            
            # Check active trades for stop/target hits (live monitoring)
            if bot.trade_tracker:
                logger.info("🔍 Checking active trades for stop/target hits...")
                current_prices = {}
                
                # Get current prices for all active trades
                active_trades = bot.trade_tracker.load_active_trades()
                for trade in active_trades:
                    if trade['status'] == 'active':
                        price = bot.data_fetcher.get_current_price(trade['symbol'])
                        if price:
                            current_prices[trade['symbol']] = price
                
                # Check for trade outcomes
                closed_count = bot.trade_tracker.check_trade_outcomes(current_prices)
                if closed_count > 0:
                    logger.info(f"🎯 {closed_count} trades closed - New signals allowed for those pairs")
                
                # Clean up expired cooldowns
                bot.trade_tracker.cleanup_expired_cooldowns()
            
            bot.run_scan_cycle()
            
            # Wait 15 minutes between scans (faster with no rate limits!)
            logger.info("⏰ Waiting 15 minutes until next scan...")
            time.sleep(15 * 60)  # 15 minutes
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()
