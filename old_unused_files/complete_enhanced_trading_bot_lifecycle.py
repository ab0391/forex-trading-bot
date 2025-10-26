#!/usr/bin/env python3
"""
ZoneSync FX Bot - Enhanced with Trade Lifecycle Management
- API Credit Optimized (83% timer reduction, smart caching, Yahoo Finance)
- Trade Lifecycle Management (prevents duplicate signals)
- Expanded Currency Pairs (10 pairs for more opportunities)
- Per-pair trade state tracking with SL/TP monitoring
"""

import os
import time
import logging
import signal
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Import caching and Yahoo Finance for API optimization
from data_cache_manager import cache_manager

# For Yahoo Finance fallback (free, no API limits)
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    print("✅ Yahoo Finance available for current prices (no API limits)")
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not available. Install with: pip install yfinance")

# Load environment variables
load_dotenv()

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/fxbot/enhanced_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradeLifecycleManager:
    """Manages trade lifecycle to prevent duplicate signals and track active trades per pair"""

    def __init__(self):
        self.active_trades_file = Path("/home/ubuntu/fxbot/active_trades.json")
        self.signals_file = Path("/home/ubuntu/fxbot/signals_history.json")
        self.active_trades = {}  # {symbol: trade_data}
        self.load_active_trades()

    def load_active_trades(self):
        """Load active trades from file"""
        try:
            if self.active_trades_file.exists():
                with open(self.active_trades_file, 'r') as f:
                    self.active_trades = json.load(f)
                logger.info(f"📊 Loaded {len(self.active_trades)} active trades")
            else:
                self.active_trades = {}
        except Exception as e:
            logger.error(f"Error loading active trades: {e}")
            self.active_trades = {}

    def save_active_trades(self):
        """Save active trades to file"""
        try:
            with open(self.active_trades_file, 'w') as f:
                json.dump(self.active_trades, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving active trades: {e}")

    def can_send_signal(self, symbol: str, entry: float, zone_type: str) -> bool:
        """Check if we can send a signal for this pair"""

        # No active trade for this pair - can send signal
        if symbol not in self.active_trades:
            return True

        active_trade = self.active_trades[symbol]

        # Check if current price has hit SL or TP (trade should be closed)
        current_price = self._get_current_price(symbol)
        if current_price and self._is_trade_closed(active_trade, current_price):
            # Trade is closed, remove from active and allow new signal
            logger.info(f"🏁 Trade closed for {symbol} - allowing new signals")
            del self.active_trades[symbol]
            self.save_active_trades()
            return True

        # Check if this is a duplicate signal (same setup)
        if self._is_duplicate_signal(active_trade, entry, zone_type):
            logger.info(f"🚫 Blocking duplicate signal for {symbol} (active trade exists)")
            return False

        # Different setup, but trade still active - don't send
        logger.info(f"⏳ Blocking new signal for {symbol} (different setup, but trade still active)")
        return False

    def register_signal(self, symbol: str, signal_data: Dict):
        """Register a new signal as active trade"""
        self.active_trades[symbol] = {
            'signal_id': signal_data['signal_id'],
            'timestamp': signal_data['timestamp'],
            'entry': signal_data['entry'],
            'stop': signal_data['stop'],
            'target': signal_data['target'],
            'zone_type': signal_data['zone_type'],
            'status': 'active'
        }
        self.save_active_trades()
        logger.info(f"✅ Registered active trade for {symbol} at {signal_data['entry']}")

    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for SL/TP monitoring"""
        try:
            # Try Yahoo Finance first (free)
            if YFINANCE_AVAILABLE:
                yf_symbol = symbol.replace('/', '') + '=X'
                ticker = yf.Ticker(yf_symbol)

                try:
                    # Try fast_info first
                    fast_info = ticker.fast_info
                    if hasattr(fast_info, 'last_price'):
                        return float(fast_info.last_price)
                except:
                    pass

                try:
                    # Try info method
                    info = ticker.info
                    if 'regularMarketPrice' in info:
                        return float(info['regularMarketPrice'])
                except:
                    pass

                try:
                    # Try history method
                    hist = ticker.history(period="1d", interval="1m")
                    if not hist.empty:
                        return float(hist['Close'].iloc[-1])
                except:
                    pass

            # Fallback: use cached price if available
            cached_price = cache_manager.get_cached_price(symbol)
            if cached_price:
                return cached_price

            return None

        except Exception as e:
            logger.warning(f"Could not get current price for {symbol}: {e}")
            return None

    def _is_trade_closed(self, trade: Dict, current_price: float) -> bool:
        """Check if trade should be closed based on current price vs SL/TP"""
        try:
            entry = trade['entry']
            stop = trade['stop']
            target = trade['target']
            zone_type = trade['zone_type']

            if zone_type == 'demand':
                # Long trade: closed if price <= stop or price >= target
                return current_price <= stop or current_price >= target
            else:
                # Short trade: closed if price >= stop or price <= target
                return current_price >= stop or current_price <= target

        except Exception as e:
            logger.error(f"Error checking trade closure: {e}")
            return False

    def _is_duplicate_signal(self, active_trade: Dict, new_entry: float, new_zone_type: str) -> bool:
        """Check if new signal is duplicate of active trade"""
        try:
            # Same zone type and entry within 5 pips = duplicate
            pip_tolerance = 0.0005  # 5 pips for most pairs

            return (active_trade['zone_type'] == new_zone_type and
                   abs(active_trade['entry'] - new_entry) < pip_tolerance)
        except:
            return False

    def force_close_trade(self, symbol: str):
        """Manually close a trade (for testing or manual intervention)"""
        if symbol in self.active_trades:
            del self.active_trades[symbol]
            self.save_active_trades()
            logger.info(f"🔧 Manually closed trade for {symbol}")

    def get_active_trades_summary(self):
        """Get summary of active trades"""
        return {
            'total_active': len(self.active_trades),
            'active_pairs': list(self.active_trades.keys()),
            'trades': self.active_trades
        }

class DataFetcher:
    """Fetch forex data from TwelveData API with optimizations"""

    def __init__(self):
        self.api_key = os.getenv("TWELVEDATA_API_KEY")
        if not self.api_key:
            raise ValueError("TWELVEDATA_API_KEY not found in environment variables")

        # Optimized data request sizes (20% reduction)
        self.optimized_outputsize = {
            "1d": 250,   # Was 300 - 250 bars = ~8 months (sufficient for daily analysis)
            "4h": 400,   # Was 500 - 400 bars = ~16 days (sufficient for 4H analysis)
            "1h": 300    # Was 1000 - 300 bars = ~12.5 days (sufficient for 1H analysis)
        }

        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info("🚀 DataFetcher optimized for API credit reduction")
        logger.info(f"📊 Reduced data requests: D1:{self.optimized_outputsize['1d']}, H4:{self.optimized_outputsize['4h']}, H1:{self.optimized_outputsize['1h']} bars")

        if YFINANCE_AVAILABLE:
            logger.info("✅ Yahoo Finance fallback enabled for current prices")

    def _get_yahoo_price(self, symbol: str) -> Optional[float]:
        """Get current price from Yahoo Finance (no API limits)"""
        if not YFINANCE_AVAILABLE:
            return None

        try:
            yf_symbol = symbol.replace('/', '') + '=X'
            ticker = yf.Ticker(yf_symbol)

            # Try multiple methods for robustness
            try:
                fast_info = ticker.fast_info
                if hasattr(fast_info, 'last_price'):
                    price = float(fast_info.last_price)
                    logger.info(f"🎯 Yahoo Finance: {symbol} = {price} (FREE)")
                    return price
            except:
                pass

            try:
                info = ticker.info
                if 'regularMarketPrice' in info:
                    price = float(info['regularMarketPrice'])
                    logger.info(f"🎯 Yahoo Finance: {symbol} = {price} (FREE)")
                    return price
            except:
                pass

            try:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    logger.info(f"🎯 Yahoo Finance: {symbol} = {price} (FREE)")
                    return price
            except:
                pass

        except Exception as e:
            logger.warning(f"Yahoo Finance failed for {symbol}: {e}")

        return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price with caching and Yahoo Finance fallback"""

        # 1. Try cache first (5 min expiry)
        cached_price = cache_manager.get_cached_price(symbol)
        if cached_price:
            return cached_price

        # 2. Try Yahoo Finance (FREE - no API limits)
        yahoo_price = self._get_yahoo_price(symbol)
        if yahoo_price:
            cache_manager.save_price_to_cache(symbol, yahoo_price)
            return yahoo_price

        # 3. Fallback to TwelveData API (uses credits)
        try:
            url = "https://api.twelvedata.com/price"
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    price = float(data['price'])
                    logger.info(f"📉 API CALL: {symbol} current price = {price} - CREDIT USED")
                    cache_manager.save_price_to_cache(symbol, price)
                    return price
            else:
                logger.error(f"TwelveData API error: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")

        return None

    def get_data(self, symbol: str, interval: str, outputsize: int = None) -> Optional[pd.DataFrame]:
        """Get forex data with smart caching and optimized request sizes"""

        # Use optimized outputsize if not specified
        if outputsize is None:
            outputsize = self.optimized_outputsize.get(interval, 300)

        # Check cache first
        cached_data = cache_manager.get_cached_data(symbol, interval, outputsize)
        if cached_data is not None:
            return cached_data

        try:
            url = "https://api.twelvedata.com/time_series"
            params = {
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': self.api_key
            }

            logger.info(f"📊 Optimized request: {symbol} {interval} {outputsize} bars")

            response = self.session.get(url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()

                if 'values' in data and data['values']:
                    logger.info(f"📉 API CALL: {symbol} {interval} ({outputsize} bars) - CREDIT USED")

                    df = pd.DataFrame(data['values'])
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df = df.sort_values('datetime').reset_index(drop=True)

                    # Convert price columns to float
                    for col in ['open', 'high', 'low', 'close']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                    # Cache the data
                    cache_manager.save_to_cache(df, symbol, interval, outputsize)

                    return df
                else:
                    logger.error(f"No data returned for {symbol} {interval}")
                    return None
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error fetching data for {symbol} {interval}: {e}")
            return None

class ZoneDetector:
    """Detect supply and demand zones"""

    def __init__(self, lookback_period=20, zone_strength_threshold=2):
        self.lookback_period = lookback_period
        self.zone_strength_threshold = zone_strength_threshold

    def detect_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect supply and demand zones"""
        zones = []

        if len(df) < self.lookback_period + 5:
            return zones

        try:
            # Calculate swing highs and lows
            df['swing_high'] = df['high'].rolling(window=self.lookback_period, center=True).max() == df['high']
            df['swing_low'] = df['low'].rolling(window=self.lookback_period, center=True).min() == df['low']

            # Detect supply zones (resistance)
            for i in range(self.lookback_period, len(df) - self.lookback_period):
                if df.iloc[i]['swing_high']:
                    zone_high = df.iloc[i]['high']
                    zone_low = df.iloc[i]['low']

                    # Check zone strength
                    touches = self._count_zone_touches(df, i, zone_high, zone_low, 'supply')

                    if touches >= self.zone_strength_threshold:
                        zones.append({
                            'type': 'supply',
                            'high': zone_high,
                            'low': zone_low,
                            'datetime': df.iloc[i]['datetime'],
                            'strength': touches,
                            'index': i
                        })

            # Detect demand zones (support)
            for i in range(self.lookback_period, len(df) - self.lookback_period):
                if df.iloc[i]['swing_low']:
                    zone_high = df.iloc[i]['high']
                    zone_low = df.iloc[i]['low']

                    # Check zone strength
                    touches = self._count_zone_touches(df, i, zone_high, zone_low, 'demand')

                    if touches >= self.zone_strength_threshold:
                        zones.append({
                            'type': 'demand',
                            'high': zone_high,
                            'low': zone_low,
                            'datetime': df.iloc[i]['datetime'],
                            'strength': touches,
                            'index': i
                        })

            return zones

        except Exception as e:
            logger.error(f"Error detecting zones: {e}")
            return []

    def _count_zone_touches(self, df: pd.DataFrame, zone_index: int, zone_high: float, zone_low: float, zone_type: str) -> int:
        """Count how many times price touched the zone"""
        touches = 0
        zone_range = zone_high - zone_low
        tolerance = zone_range * 0.1  # 10% tolerance

        # Look for touches after the zone formation
        for i in range(zone_index + 1, len(df)):
            if zone_type == 'supply':
                # For supply zones, look for price reaching the zone from below
                if (df.iloc[i]['high'] >= zone_low - tolerance and
                    df.iloc[i]['high'] <= zone_high + tolerance):
                    touches += 1
            else:
                # For demand zones, look for price reaching the zone from above
                if (df.iloc[i]['low'] <= zone_high + tolerance and
                    df.iloc[i]['low'] >= zone_low - tolerance):
                    touches += 1

        return touches

    def get_active_zones(self, df: pd.DataFrame, current_price: float) -> List[Dict[str, Any]]:
        """Get zones that are currently relevant for trading"""
        all_zones = self.detect_zones(df)
        active_zones = []

        price_tolerance = current_price * 0.02  # 2% tolerance

        for zone in all_zones:
            # Check if current price is near the zone
            if zone['type'] == 'supply' and current_price >= zone['low'] - price_tolerance:
                if current_price <= zone['high'] + price_tolerance:
                    active_zones.append(zone)
            elif zone['type'] == 'demand' and current_price <= zone['high'] + price_tolerance:
                if current_price >= zone['low'] - price_tolerance:
                    active_zones.append(zone)

        # Sort by strength and recency
        active_zones.sort(key=lambda x: (x['strength'], x['index']), reverse=True)
        return active_zones[:3]  # Return top 3 zones

class H4BiasAnalyzer:
    """Analyze H4 timeframe for bias confirmation"""

    def __init__(self):
        pass

    def analyze_h4_bias(self, df_h4: pd.DataFrame) -> Dict[str, Any]:
        """Analyze H4 bias using multiple factors"""

        if len(df_h4) < 50:
            return {'bias': 'neutral', 'confidence': 0}

        try:
            # Get recent data
            recent_data = df_h4.tail(50).copy()

            # Calculate EMAs
            recent_data['ema_20'] = recent_data['close'].ewm(span=20).mean()
            recent_data['ema_50'] = recent_data['close'].ewm(span=50).mean()
            recent_data['ema_200'] = recent_data['close'].ewm(span=200).mean()

            # Calculate RSI
            delta = recent_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            recent_data['rsi'] = 100 - (100 / (1 + rs))

            # Latest values
            latest = recent_data.iloc[-1]
            current_price = latest['close']
            ema_20 = latest['ema_20']
            ema_50 = latest['ema_50']
            ema_200 = latest['ema_200']
            current_rsi = latest['rsi']

            # Bias factors
            bullish_factors = 0
            bearish_factors = 0

            # 1. EMA alignment
            if ema_20 > ema_50 > ema_200:
                bullish_factors += 2
            elif ema_20 < ema_50 < ema_200:
                bearish_factors += 2

            # 2. Price vs EMAs
            if current_price > ema_20:
                bullish_factors += 1
            else:
                bearish_factors += 1

            # 3. RSI levels
            if current_rsi < 30:
                bullish_factors += 1  # Oversold, potential bounce
            elif current_rsi > 70:
                bearish_factors += 1  # Overbought, potential drop

            # 4. Recent trend
            price_5_ago = recent_data.iloc[-6]['close'] if len(recent_data) >= 6 else current_price
            if current_price > price_5_ago:
                bullish_factors += 1
            else:
                bearish_factors += 1

            # 5. Momentum
            if recent_data['close'].tail(3).is_monotonic_increasing:
                bullish_factors += 1
            elif recent_data['close'].tail(3).is_monotonic_decreasing:
                bearish_factors += 1

            # Determine bias
            total_factors = bullish_factors + bearish_factors
            if total_factors == 0:
                bias = 'neutral'
                confidence = 0
            else:
                confidence = max(bullish_factors, bearish_factors) / total_factors * 100

                if bullish_factors > bearish_factors:
                    bias = 'bullish'
                elif bearish_factors > bullish_factors:
                    bias = 'bearish'
                else:
                    bias = 'neutral'

            return {
                'bias': bias,
                'confidence': round(confidence, 0),
                'bullish_factors': bullish_factors,
                'bearish_factors': bearish_factors,
                'current_rsi': current_rsi,
                'ema_stack': f"EMA20:{ema_20:.5f} EMA50:{ema_50:.5f} EMA200:{ema_200:.5f}"
            }

        except Exception as e:
            logger.error(f"Error analyzing H4 bias: {e}")
            return {'bias': 'neutral', 'confidence': 0}

class TelegramNotifier:
    """Send notifications via Telegram"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not found. Notifications disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Telegram notifications enabled")

    def send_signal(self, symbol: str, zone_type: str, entry: float, stop: float, target: float,
                   h4_bias: Dict, d1_bias: str, risk_reward: float) -> bool:
        """Send trading signal notification"""

        if not self.enabled:
            logger.info("Telegram disabled - signal logged only")
            return True

        try:
            # Format message
            direction = "🟢 LONG" if zone_type == "demand" else "🔴 SHORT"

            message = f"""
🎯 **ZONESYNC SIGNAL** 🎯

{direction} {symbol}

📈 **Entry:** {entry}
🛑 **Stop:** {stop}
🎯 **Target:** {target}
📊 **R:R:** {risk_reward}

**H4 Bias:** {h4_bias['bias'].upper()} ({h4_bias['confidence']}%)
**D1 Bias:** {d1_bias.upper()}

**RSI:** {h4_bias.get('current_rsi', 'N/A'):.1f}
**Factors:** 🟢{h4_bias['bullish_factors']} vs 🔴{h4_bias['bearish_factors']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                logger.info(f"📱 Signal sent for {symbol}")
                return True
            else:
                logger.error(f"Telegram error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False

class TradeTracker:
    """Automatic trade tracking and performance analytics with lifecycle management"""

    def __init__(self):
        self.signals_file = Path("/home/ubuntu/fxbot/signals_history.json")
        self.load_signals()

    def load_signals(self):
        """Load existing signals history"""
        try:
            if self.signals_file.exists():
                with open(self.signals_file, 'r') as f:
                    self.signals = json.load(f)
            else:
                self.signals = []
        except Exception as e:
            logger.error(f"Error loading signals history: {e}")
            self.signals = []

    def save_signals(self):
        """Save signals to file"""
        try:
            with open(self.signals_file, 'w') as f:
                json.dump(self.signals, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving signals: {e}")

    def record_signal(self, symbol: str, zone_type: str, entry: float,
                     stop: float, target: float, risk_reward: float,
                     d1_bias: str, h4_bias: Dict[str, Any]) -> str:
        """Record a new signal with lifecycle tracking"""

        signal_id = f"{symbol.replace('/', '')}_{zone_type}_{int(time.time())}"

        signal_data = {
            'signal_id': signal_id,
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'zone_type': zone_type,
            'entry': entry,
            'stop': stop,
            'target': target,
            'risk_reward': risk_reward,
            'd1_bias': d1_bias,
            'h4_bias': h4_bias,
            'status': 'active',
            'outcome': None,
            'pnl': None
        }

        self.signals.append(signal_data)
        self.save_signals()

        logger.info(f"📊 Signal recorded: {signal_id}")
        return signal_id

class EnhancedTradingBot:
    """Main trading bot with lifecycle management and expanded pairs"""

    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.zone_detector = ZoneDetector()
        self.h4_analyzer = H4BiasAnalyzer()
        self.notifier = TelegramNotifier()
        self.tracker = TradeTracker()
        self.lifecycle_manager = TradeLifecycleManager()

        # EXPANDED CURRENCY PAIRS (10 pairs for more opportunities)
        self.symbols = [
            # Original 5 Major Pairs
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF",
            # Added 5 High-Quality Pairs
            "NZD/USD",  # Kiwi - good range trading
            "USD/CAD",  # Oil correlation, good volatility
            "EUR/GBP",  # Popular cross with clean zones
            "EUR/JPY",  # High volatility, excellent for zones
            "GBP/JPY"   # Very volatile, clear zone setups
        ]

        self.shutdown_requested = False

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        logger.info(f"🚀 Enhanced Trading Bot initialized with {len(self.symbols)} pairs")
        logger.info(f"📊 Pairs: {', '.join(self.symbols)}")
        logger.info(f"🔄 Trade lifecycle management enabled")

    def _signal_handler(self, signum, frame):
        logger.info(f"Shutdown signal {signum} received")
        self.shutdown_requested = True

    def analyze_pair(self, symbol: str) -> Optional[Dict]:
        """Analyze a single currency pair for trading opportunities"""

        logger.info(f"Scanning {symbol}...")

        try:
            # Get current price for lifecycle checking
            current_price = self.data_fetcher.get_current_price(symbol)
            if not current_price:
                logger.warning(f"Could not get current price for {symbol}")
                return None

            # Get market data
            d1_data = self.data_fetcher.get_data(symbol, "1d")
            h4_data = self.data_fetcher.get_data(symbol, "4h")
            h1_data = self.data_fetcher.get_data(symbol, "1h")

            if d1_data is None or h4_data is None or h1_data is None:
                logger.warning(f"Insufficient data for {symbol}")
                return None

            # Analyze D1 bias (simple trend)
            d1_bias = "bullish" if d1_data['close'].iloc[-1] > d1_data['close'].iloc[-5] else "bearish"

            # Analyze H4 bias
            h4_bias = self.h4_analyzer.analyze_h4_bias(h4_data)

            # Detect zones on H1
            zones = self.zone_detector.get_active_zones(h1_data, current_price)

            if not zones:
                return None

            # Find the best zone
            best_zone = zones[0]
            zone_type = best_zone['type']

            # Calculate entry, stop, and target
            if zone_type == 'demand':
                entry = best_zone['high']
                stop = best_zone['low'] * 0.999  # 0.1% below zone
                target = entry + (entry - stop) * 2  # 2:1 R:R
            else:
                entry = best_zone['low']
                stop = best_zone['high'] * 1.001  # 0.1% above zone
                target = entry - (stop - entry) * 2  # 2:1 R:R

            risk_reward = abs(target - entry) / abs(entry - stop)

            # Filter trades: H4 bias must align with trade direction
            if zone_type == 'demand' and h4_bias['bias'] != 'bullish':
                return None
            if zone_type == 'supply' and h4_bias['bias'] != 'bearish':
                return None

            # CHECK TRADE LIFECYCLE - Can we send this signal?
            if not self.lifecycle_manager.can_send_signal(symbol, entry, zone_type):
                return None  # Signal blocked - active trade exists or duplicate

            # Generate signal
            signal_data = {
                'symbol': symbol,
                'zone_type': zone_type,
                'entry': entry,
                'stop': stop,
                'target': target,
                'risk_reward': risk_reward,
                'd1_bias': d1_bias,
                'h4_bias': h4_bias,
                'current_price': current_price,
                'zone_strength': best_zone['strength']
            }

            return signal_data

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None

    def run_scan(self):
        """Run enhanced trading scan with lifecycle management"""

        logger.info("🚀 Starting API CREDIT OPTIMIZED trading scan...")
        logger.info("💡 Optimizations: Timer 30min, Cache 15-60min, Yahoo Finance")
        logger.info(f"🔄 Trade lifecycle management active for {len(self.symbols)} pairs")

        # Clean expired cache files to maintain performance
        cache_manager.clear_expired_cache()

        # Show active trades summary
        active_summary = self.lifecycle_manager.get_active_trades_summary()
        logger.info(f"📊 Active trades: {active_summary['total_active']}/{len(self.symbols)} - {active_summary['active_pairs']}")

        signals_sent = 0
        api_calls_made = 0

        for symbol in self.symbols:
            if self.shutdown_requested:
                break

            try:
                signal_data = self.analyze_pair(symbol)

                if signal_data:
                    # Record signal
                    signal_id = self.tracker.record_signal(
                        signal_data['symbol'],
                        signal_data['zone_type'],
                        signal_data['entry'],
                        signal_data['stop'],
                        signal_data['target'],
                        signal_data['risk_reward'],
                        signal_data['d1_bias'],
                        signal_data['h4_bias']
                    )

                    # Register with lifecycle manager
                    signal_record = {
                        'signal_id': signal_id,
                        'timestamp': datetime.now().isoformat(),
                        'entry': signal_data['entry'],
                        'stop': signal_data['stop'],
                        'target': signal_data['target'],
                        'zone_type': signal_data['zone_type']
                    }
                    self.lifecycle_manager.register_signal(symbol, signal_record)

                    # Send notification
                    success = self.notifier.send_signal(
                        signal_data['symbol'],
                        signal_data['zone_type'],
                        signal_data['entry'],
                        signal_data['stop'],
                        signal_data['target'],
                        signal_data['h4_bias'],
                        signal_data['d1_bias'],
                        signal_data['risk_reward']
                    )

                    if success:
                        signals_sent += 1
                        logger.info(f"✅ Signal sent for {symbol}")
                    else:
                        logger.warning(f"⚠️ Failed to send signal for {symbol}")

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue

        # Performance summary
        final_summary = self.lifecycle_manager.get_active_trades_summary()
        logger.info(f"Scan complete. Signals sent: {signals_sent}")
        logger.info(f"📊 Final active trades: {final_summary['total_active']}/{len(self.symbols)}")
        logger.info(f"Performance: {'signals_sent': {signals_sent}, 'pairs_scanned': {len(self.symbols)}, 'active_trades': {final_summary['total_active']}}")
        logger.info("Scan completed successfully.")

def run_once():
    """Run the enhanced trading bot once with lifecycle management"""
    try:
        bot = EnhancedTradingBot()
        bot.run_scan()
    except Exception as e:
        logger.error(f"Critical error in main execution: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    run_once()