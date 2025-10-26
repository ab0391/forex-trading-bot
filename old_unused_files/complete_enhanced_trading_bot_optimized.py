#!/usr/bin/env python3
"""
ZoneSync FX Bot - API Credit Optimized Version
- 83% reduction: Timer frequency 5min → 30min
- 50% reduction: Smart data caching (15-30min reuse)
- Yahoo Finance fallback for current prices (no API limits)
- Optimized data requests (reduced outputsize)
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

# Load environment variables
load_dotenv()

# Setup comprehensive logging
log_file = '/home/ubuntu/fxbot/enhanced_bot.log' if os.path.exists('/home/ubuntu/fxbot/') else '/tmp/enhanced_bot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import caching and Yahoo Finance for API optimization
from data_cache_manager import cache_manager

# Import rate limiter for TwelveData API
from rate_limiter import enhanced_rate_limiter

# For Yahoo Finance fallback (free, no API limits)
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    logger.info("✅ Yahoo Finance available for current prices (no API limits)")
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("⚠️  yfinance not available. Install with: pip install yfinance")

class TelegramNotifier:
    """Telegram-only notification system with spam prevention"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.session = self._create_session()
        self.last_signals = {}  # Track last signal per symbol to prevent spam

    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send message to Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured - skipping notification")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            return False

    def send_trading_alert(self, symbol: str, zone_type: str, entry: float,
                          stop: float, target: float, rr: float, bias_info: str, current_price: float = None) -> bool:
        """Send trading signal alert with spam prevention"""

        # Create signal fingerprint to prevent duplicates
        signal_key = f"{symbol}_{zone_type}_{entry:.5f}_{stop:.5f}_{target:.5f}"
        current_time = time.time()

        # Check if we sent this exact signal recently (within 1 hour)
        if signal_key in self.last_signals:
            time_diff = current_time - self.last_signals[signal_key]
            if time_diff < 3600:  # 1 hour cooldown
                logger.info(f"Skipping duplicate signal for {symbol} (sent {time_diff:.0f}s ago)")
                return False

        # Record this signal
        self.last_signals[signal_key] = current_time

        direction = "🟢 LONG" if zone_type.lower() == "demand" else "🔴 SHORT"

        # Calculate distance from current price if available
        price_info = ""
        if current_price is not None:
            distance = abs(current_price - entry) * 10000  # Convert to pips
            direction_text = "above" if current_price > entry else "below"
            price_info = f"""
💰 *Current Price:* `{current_price:.5f}`
📏 *Distance to Entry:* {distance:.1f} pips {direction_text}"""

        message = f"""
🚨 *ZoneSync Trading Alert* 🚨

📊 *{symbol}* | {direction}
⚡ *Strategy:* Multi-Timeframe Zone{price_info}

📈 *Setup Details:*
• Entry: `{entry:.5f}`
• Stop Loss: `{stop:.5f}`
• Take Profit: `{target:.5f}`
• Risk/Reward: `{rr:.1f}R`

🎯 *Bias Stack:*
{bias_info}

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

💡 *Action:* Monitor for entry confirmation
        """.strip()

        success = self.send_message(message)

        # Clean up old signals (older than 24 hours)
        cutoff_time = current_time - 86400  # 24 hours
        self.last_signals = {k: v for k, v in self.last_signals.items() if v > cutoff_time}

        return success

    def send_retest_alert(self, symbol: str, zone_type: str, entry: float, rr: float) -> bool:
        """Send zone retest alert"""

        direction = "🟢 LONG" if zone_type.lower() == "demand" else "🔴 SHORT"

        message = f"""
🎯 *Zone Retest Alert* 🎯

📊 *{symbol}* | {direction}
⚡ *Entry Level Touched:* `{entry:.5f}`
📊 *Risk/Reward:* `{rr:.1f}R`

🚀 *Action:* First retest - consider entry per plan

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """.strip()

        return self.send_message(message)

class H4BiasAnalyzer:
    """H4 timeframe bias analysis for signal filtering"""

    def __init__(self):
        self.ema_periods = [20, 50, 200]
        self.rsi_period = 14

    def calculate_bias(self, h4_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate H4 bias with confidence scoring"""

        if len(h4_df) < 200:
            return {"bias": "insufficient_data", "confidence": 0, "details": "Not enough data"}

        try:
            close = h4_df['close']

            # Calculate EMAs
            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()
            ema200 = close.ewm(span=200).mean()

            # Calculate RSI
            rsi = self._calculate_rsi(close, self.rsi_period)

            # Current values
            current_price = close.iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_ema200 = ema200.iloc[-1]
            current_rsi = rsi.iloc[-1]

            # Bias determination
            bullish_factors = 0
            bearish_factors = 0

            # Factor 1: EMA stack
            if current_ema20 > current_ema50 > current_ema200:
                bullish_factors += 3
            elif current_ema20 < current_ema50 < current_ema200:
                bearish_factors += 3

            # Factor 2: Price vs EMAs
            if current_price > current_ema200:
                bullish_factors += 2
            elif current_price < current_ema200:
                bearish_factors += 2

            # Factor 3: EMA slopes
            ema20_slope = (ema20.iloc[-1] - ema20.iloc[-5]) / 5
            if ema20_slope > 0:
                bullish_factors += 1
            else:
                bearish_factors += 1

            # Factor 4: RSI conditions
            if 40 < current_rsi < 80:
                bullish_factors += 1
            elif 20 < current_rsi < 60:
                bearish_factors += 1

            # Determine bias
            if bullish_factors > bearish_factors and bullish_factors >= 4:
                bias = "bullish"
                confidence = min(bullish_factors * 15, 100)
            elif bearish_factors > bullish_factors and bearish_factors >= 4:
                bias = "bearish"
                confidence = min(bearish_factors * 15, 100)
            else:
                bias = "neutral"
                confidence = 40

            return {
                "bias": bias,
                "confidence": confidence,
                "bullish_factors": bullish_factors,
                "bearish_factors": bearish_factors,
                "current_rsi": current_rsi,
                "ema_stack": f"EMA20:{current_ema20:.5f} EMA50:{current_ema50:.5f} EMA200:{current_ema200:.5f}"
            }

        except Exception as e:
            logger.error(f"H4 bias calculation error: {e}")
            return {"bias": "error", "confidence": 0, "details": str(e)}

    def _calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class TradeTracker:
    """Automatic trade tracking and performance analytics"""

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
            logger.error(f"Error saving signals history: {e}")

    def record_signal(self, symbol: str, zone_type: str, entry: float,
                     stop: float, target: float, rr: float, d1_bias: str,
                     h4_bias: Dict[str, Any]) -> str:
        """Record new trading signal"""

        signal_id = f"{symbol}_{zone_type}_{int(time.time())}"

        signal = {
            "signal_id": signal_id,
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "zone_type": zone_type,
            "entry": entry,
            "stop": stop,
            "target": target,
            "risk_reward": rr,
            "d1_bias": d1_bias,
            "h4_bias": h4_bias,
            "status": "active",
            "outcome": None,
            "pnl": None
        }

        self.signals.append(signal)
        self.save_signals()

        logger.info(f"Recorded signal: {signal_id}")
        return signal_id

    def get_performance_stats(self) -> Dict[str, Any]:
        """Calculate performance statistics"""

        if not self.signals:
            return {"total_signals": 0, "message": "No signals recorded yet"}

        total_signals = len(self.signals)
        active_signals = len([s for s in self.signals if s["status"] == "active"])

        # Calculate stats for completed signals (you'll update these manually)
        completed_signals = [s for s in self.signals if s.get("outcome")]

        if completed_signals:
            wins = len([s for s in completed_signals if s["outcome"] == "win"])
            losses = len([s for s in completed_signals if s["outcome"] == "loss"])
            win_rate = (wins / len(completed_signals)) * 100

            total_pnl = sum([s.get("pnl", 0) for s in completed_signals])
            avg_rr = sum([s["risk_reward"] for s in completed_signals]) / len(completed_signals)
        else:
            wins = losses = win_rate = total_pnl = avg_rr = 0

        return {
            "total_signals": total_signals,
            "active_signals": active_signals,
            "completed_signals": len(completed_signals),
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 1),
            "total_pnl": total_pnl,
            "average_rr": round(avg_rr, 1)
        }

class DataFetcher:
    """API Credit Optimized Data Fetcher
    - Smart caching (15-30min reuse)
    - Yahoo Finance fallback for current prices
    - Reduced data requests (300 vs 1000 bars)
    """

    def __init__(self):
        self.td_key = os.getenv("TWELVEDATA_API_KEY")
        self.session = self._create_session()
        self.rate_limit_sleep = 65

        # API Credit Optimization Settings
        self.optimized_outputsize = {
            "1d": 250,   # Reduced from 300 (sufficient for daily analysis)
            "4h": 400,   # Reduced from 500 (16 days of 4H data)
            "1h": 300    # Reduced from 1000 (12.5 days of 1H data)
        }

        logger.info("🚀 DataFetcher optimized for API credit reduction")
        logger.info(f"📊 Reduced data requests: D1:{self.optimized_outputsize['1d']}, H4:{self.optimized_outputsize['4h']}, H1:{self.optimized_outputsize['1h']}")
        logger.info("🛡️ Rate limiter enabled: max 7 calls/minute (vs TwelveData limit of 8)")

        if YFINANCE_AVAILABLE:
            logger.info("✅ Yahoo Finance fallback enabled for current prices")

    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Fetch current market price - OPTIMIZED with Yahoo Finance fallback"""

        # 🎯 Step 1: Check cache first (5-minute cache)
        cached_price = cache_manager.get_cached_price(symbol)
        if cached_price is not None:
            return cached_price

        # 🚀 Step 2: Try Yahoo Finance first (FREE, NO API LIMITS!)
        if YFINANCE_AVAILABLE:
            yahoo_price = self._get_yahoo_price(symbol)
            if yahoo_price is not None:
                cache_manager.save_price_to_cache(symbol, yahoo_price)
                return yahoo_price

        # 📊 Step 3: Fallback to TwelveData (uses API credits)
        logger.info(f"📉 Falling back to TwelveData for {symbol} current price")
        
        # 🛡️ RATE LIMITER: Wait before making TwelveData API call
        enhanced_rate_limiter.wait_for_api_call("TwelveData")
        
        td_price = self._get_twelvedata_price(symbol)
        if td_price is not None:
            cache_manager.save_price_to_cache(symbol, td_price)

        return td_price

    def _get_yahoo_price(self, symbol: str) -> Optional[float]:
        """Get current price from Yahoo Finance (FREE)"""
        try:
            # Convert to Yahoo Finance format
            yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)

            # Try multiple methods for current price
            try:
                info = ticker.info
                if 'regularMarketPrice' in info and info['regularMarketPrice']:
                    price = float(info['regularMarketPrice'])
                    logger.info(f"🎯 Yahoo Finance: {symbol} = {price:.5f} (FREE)")
                    return price
            except:
                pass

            try:
                fast_info = ticker.fast_info
                if hasattr(fast_info, 'last_price') and fast_info.last_price:
                    price = float(fast_info.last_price)
                    logger.info(f"🎯 Yahoo Finance Fast: {symbol} = {price:.5f} (FREE)")
                    return price
            except:
                pass

            try:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    logger.info(f"🎯 Yahoo Finance Hist: {symbol} = {price:.5f} (FREE)")
                    return price
            except:
                pass

        except Exception as e:
            logger.warning(f"⚠️  Yahoo Finance failed for {symbol}: {e}")

        return None

    def _convert_to_yahoo_symbol(self, symbol: str) -> str:
        """Convert forex symbol to Yahoo Finance format"""
        symbol_clean = symbol.replace("/", "")
        yahoo_symbols = {
            "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X",
            "AUDUSD": "AUDUSD=X", "USDCHF": "USDCHF=X", "USDCAD": "USDCAD=X",
            "NZDUSD": "NZDUSD=X", "EURJPY": "EURJPY=X", "GBPJPY": "GBPJPY=X"
        }
        return yahoo_symbols.get(symbol_clean, f"{symbol_clean}=X")

    def _get_twelvedata_price(self, symbol: str) -> Optional[float]:
        """Get current price from TwelveData (USES API CREDITS)"""

        if not self.td_key:
            logger.error("TWELVEDATA_API_KEY missing")
            return None

        symbol_formatted = symbol.replace("/", "")
        params = {"symbol": symbol_formatted, "apikey": self.td_key}
        url = "https://api.twelvedata.com/price"

        try:
            response = self.session.get(url, params=params, timeout=(5, 10))
            response.raise_for_status()
            data = response.json()

            if "price" in data:
                price = float(data["price"])
                logger.info(f"📊 TwelveData: {symbol} = {price:.5f} (API CREDIT USED)")
                return price
            else:
                logger.error(f"No TwelveData price for {symbol}: {data}")
                return None

        except Exception as e:
            logger.error(f"TwelveData price error for {symbol}: {e}")
            return None

    def fetch_data(self, symbol: str, interval: str, outputsize: int = 5000) -> Optional[pd.DataFrame]:
        """Fetch data with SMART CACHING and OPTIMIZED sizes"""

        # 🎯 Step 1: Use optimized outputsize to reduce API credits
        optimized_size = self.optimized_outputsize.get(interval, outputsize)
        if optimized_size != outputsize:
            logger.info(f"📊 Optimized request: {symbol} {interval} {outputsize}→{optimized_size} bars")

        # 🎯 Step 2: Check cache first (15-60min cache depending on timeframe)
        cached_data = cache_manager.get_cached_data(symbol, interval, optimized_size)
        if cached_data is not None:
            return cached_data

        # 🎯 Step 3: Fetch from TwelveData (uses API credits)
        logger.info(f"📉 API CALL: {symbol} {interval} ({optimized_size} bars) - CREDIT USED")

        # 🛡️ RATE LIMITER: Wait before making TwelveData API call
        enhanced_rate_limiter.wait_for_api_call("TwelveData")

        if not self.td_key:
            logger.error("TWELVEDATA_API_KEY missing")
            return None

        interval_map = {
            "1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min",
            "1h": "1h", "4h": "4h", "1d": "1day", "1w": "1week"
        }

        params = {
            "symbol": symbol,
            "interval": interval_map.get(interval, interval),
            "apikey": self.td_key,
            "outputsize": optimized_size,  # Use optimized size
            "timezone": "UTC",
            "format": "JSON",
            "order": "ASC",
        }

        url = "https://api.twelvedata.com/time_series"

        try:
            response = self.session.get(url, params=params, timeout=(10, 30))
            response.raise_for_status()

            data = response.json()

            if "values" not in data:
                error_msg = data.get("message", str(data))
                if "API credits" in error_msg or "limit" in error_msg.lower():
                    logger.warning(f"🚨 RATE LIMIT HIT: {error_msg}")
                    if "daily" in error_msg.lower():
                        logger.error("🚨 DAILY LIMIT EXCEEDED - Bot will retry later")
                        return None
                    logger.info(f"⏳ Rate limit sleep: {self.rate_limit_sleep}s")
                    time.sleep(self.rate_limit_sleep)
                return None

            df = pd.DataFrame(data["values"])
            if df.empty:
                return None

            # Convert data types
            df["datetime"] = pd.to_datetime(df["datetime"])
            for col in ["open", "high", "low", "close", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.sort_values("datetime").reset_index(drop=True)

            # 🎯 Step 4: Save to cache for future use
            cache_manager.save_to_cache(df, symbol, interval, optimized_size)

            return df

        except Exception as e:
            logger.error(f"Data fetch error for {symbol}: {e}")
            return None

class ZoneDetector:
    """Enhanced zone detection with improved filtering"""

    def __init__(self):
        self.min_rr = 2.0
        self.base_min = 2
        self.base_max = 6
        self.atr_period = 14

    def find_zones(self, symbol: str, h1_df: pd.DataFrame, d1_bias: str, h4_bias: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find zones using original logic with H4 filtering and deduplication"""

        zones = []

        if len(h1_df) < 100:
            return zones

        try:
            # Calculate ATR for dynamic sizing
            atr = self._calculate_atr(h1_df, self.atr_period)
            current_atr = atr.iloc[-1]

            # Scan for zones (simplified from original logic)
            potential_zones = []

            for i in range(50, len(h1_df) - 10):
                zone = self._check_zone_formation(h1_df, i, current_atr)

                if zone:
                    zone["symbol"] = symbol

                    # Apply H4 bias filtering
                    if self._should_take_zone(zone, d1_bias, h4_bias):
                        potential_zones.append(zone)

            # Deduplicate zones that are too close together
            zones = self._deduplicate_zones(potential_zones, current_atr)

            return zones

        except Exception as e:
            logger.error(f"Zone detection error for {symbol}: {e}")
            return zones

    def _deduplicate_zones(self, zones: List[Dict[str, Any]], atr: float) -> List[Dict[str, Any]]:
        """Remove zones that are too close together"""

        if len(zones) <= 1:
            return zones

        # Group zones by type
        demand_zones = [z for z in zones if z["type"] == "demand"]
        supply_zones = [z for z in zones if z["type"] == "supply"]

        # Deduplicate each type separately
        unique_demand = self._deduplicate_by_proximity(demand_zones, atr)
        unique_supply = self._deduplicate_by_proximity(supply_zones, atr)

        return unique_demand + unique_supply

    def _deduplicate_by_proximity(self, zones: List[Dict[str, Any]], atr: float) -> List[Dict[str, Any]]:
        """Remove zones that are within 1 ATR of each other, keeping the best one"""

        if len(zones) <= 1:
            return zones

        # Sort by risk/reward ratio (best first)
        zones.sort(key=lambda z: z["rr"], reverse=True)

        unique_zones = []
        min_distance = atr * 1.0  # Minimum 1 ATR between zones

        for zone in zones:
            is_too_close = False

            for existing_zone in unique_zones:
                distance = abs(zone["entry"] - existing_zone["entry"])
                if distance < min_distance:
                    is_too_close = True
                    break

            if not is_too_close:
                unique_zones.append(zone)

        return unique_zones

    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate ATR"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()

    def _check_zone_formation(self, df: pd.DataFrame, index: int, atr: float) -> Optional[Dict[str, Any]]:
        """Check for zone formation at given index"""

        try:
            # Get potential base candles
            base_start = max(0, index - self.base_max)
            base_end = index
            base_candles = df.iloc[base_start:base_end]

            if len(base_candles) < self.base_min:
                return None

            # Check base characteristics
            base_high = base_candles['high'].max()
            base_low = base_candles['low'].min()
            base_range = base_high - base_low

            # Base range check
            if base_range > 1.2 * atr:
                return None

            # Check for breakout
            breakout_candle = df.iloc[index]

            # Bullish breakout (demand zone)
            if breakout_candle['close'] > base_high + (0.2 * atr):
                entry = base_high
                stop = base_low - (0.1 * atr)
                risk = entry - stop
                target = entry + (self.min_rr * risk)
                rr = self.min_rr

                return {
                    "type": "demand",
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "rr": rr,
                    "formed_at": df.iloc[index]['datetime'],
                    "freshness_minutes": 0
                }

            # Bearish breakout (supply zone)
            elif breakout_candle['close'] < base_low - (0.2 * atr):
                entry = base_low
                stop = base_high + (0.1 * atr)
                risk = stop - entry
                target = entry - (self.min_rr * risk)
                rr = self.min_rr

                return {
                    "type": "supply",
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "rr": rr,
                    "formed_at": df.iloc[index]['datetime'],
                    "freshness_minutes": 0
                }

        except Exception as e:
            logger.error(f"Zone formation check error: {e}")

        return None

    def _should_take_zone(self, zone: Dict[str, Any], d1_bias: str, h4_bias: Dict[str, Any]) -> bool:
        """Filter zones based on bias alignment"""

        # H4 bias confidence requirement
        if h4_bias.get("confidence", 0) < 60:
            return False

        zone_type = zone["type"]
        h4_bias_direction = h4_bias.get("bias", "neutral")

        # Bullish alignment check
        if d1_bias == "bullish" and zone_type == "demand":
            return h4_bias_direction in ["bullish", "neutral"]

        # Bearish alignment check
        elif d1_bias == "bearish" and zone_type == "supply":
            return h4_bias_direction in ["bearish", "neutral"]

        return False

class EnhancedTradingBot:
    """Main trading bot with all enhancements and spam prevention"""

    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.zone_detector = ZoneDetector()
        self.h4_analyzer = H4BiasAnalyzer()
        self.notifier = TelegramNotifier()
        self.tracker = TradeTracker()

        # 🎯 SMART SYMBOL ROTATION: All major pairs covered across multiple cycles
        # Strategy: 2 symbols per cycle to stay under 8/minute limit, but rotate through ALL pairs
        self.all_symbols = [
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF",  # Original 5
            "EUR/GBP", "GBP/JPY", "EUR/JPY", "AUD/JPY", "NZD/USD"   # Additional major pairs
        ]
        self.symbols_per_cycle = 2  # Max 2 symbols per scan = 8 API calls
        self.scan_count = 0
        self.shutdown_requested = False

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info(f"Shutdown signal {signum} received")
        self.shutdown_requested = True

    def calculate_daily_bias(self, d1_df: pd.DataFrame) -> str:
        """Calculate D1 bias using original logic"""

        if len(d1_df) < 200:
            return "none"

        try:
            close = d1_df['close']
            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()
            ema200 = close.ewm(span=200).mean()

            current_close = close.iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_ema200 = ema200.iloc[-1]

            # Bullish conditions
            if (current_close > current_ema200 and
                current_ema20 > current_ema50 > current_ema200):
                return "bullish"

            # Bearish conditions
            elif (current_close < current_ema200 and
                  current_ema20 < current_ema50 < current_ema200):
                return "bearish"

            return "none"

        except Exception as e:
            logger.error(f"D1 bias calculation error: {e}")
            return "none"

    def get_symbols_for_current_scan(self):
        """Get symbols for current scan cycle with smart rotation"""
        start_idx = (self.scan_count * self.symbols_per_cycle) % len(self.all_symbols)
        end_idx = min(start_idx + self.symbols_per_cycle, len(self.all_symbols))
        
        symbols = self.all_symbols[start_idx:end_idx]
        
        # If we reach the end and don't have enough symbols, wrap around
        if len(symbols) < self.symbols_per_cycle and start_idx + self.symbols_per_cycle > len(self.all_symbols):
            remaining_needed = self.symbols_per_cycle - len(symbols)
            symbols.extend(self.all_symbols[:remaining_needed])
        
        total_cycles_for_all_symbols = (len(self.all_symbols) + self.symbols_per_cycle - 1) // self.symbols_per_cycle
        cycle_in_rotation = self.scan_count % total_cycles_for_all_symbols + 1
        
        logger.info(f"🎯 Scan cycle {self.scan_count + 1} (Rotation {cycle_in_rotation}/{total_cycles_for_all_symbols}): Processing {symbols}")
        logger.info(f"📊 Coverage: All {len(self.all_symbols)} pairs scanned every {total_cycles_for_all_symbols} cycles")
        
        return symbols

    def run_scan(self):
        """Run API OPTIMIZED trading scan with SMART SYMBOL ROTATION"""

        logger.info("🚀 Starting SYMBOL-ROTATED trading scan...")
        logger.info("💡 Strategy: 2 symbols per cycle, all major pairs covered via rotation")

        # Get symbols for this specific scan cycle
        current_symbols = self.get_symbols_for_current_scan()

        # Clean expired cache files to maintain performance
        cache_manager.clear_expired_cache()

        signals_sent = 0
        api_calls_made = 0

        for symbol_index, symbol in enumerate(current_symbols):
            if self.shutdown_requested:
                break

            try:
                logger.info(f"Scanning {symbol}... ({symbol_index + 1}/{len(current_symbols)})")

                # 🛡️ INTER-SYMBOL DELAY: Add 15-second gap between symbols to spread API calls
                if symbol_index > 0:  # Skip delay for first symbol
                    logger.info(f"⏰ Inter-symbol delay: 15 seconds to distribute API calls...")
                    time.sleep(15)

                # Fetch multi-timeframe data with OPTIMIZED sizes + ENHANCED CACHING
                # Cache strategy: D1 (60min), H4 (30min), H1 (15min) to minimize API calls
                # Reduced outputsize: D1:250, H4:400, H1:300 (vs original 300,500,1000)
                logger.info(f"📊 Fetching timeframe data for {symbol} (cache-first strategy)...")
                
                d1_data = self.data_fetcher.fetch_data(symbol, "1d")  # Cache: 60min, API: last resort
                h4_data = self.data_fetcher.fetch_data(symbol, "4h")  # Cache: 30min, API: last resort  
                h1_data = self.data_fetcher.fetch_data(symbol, "1h")  # Cache: 15min, API: last resort

                if not all([d1_data is not None, h4_data is not None, h1_data is not None]):
                    logger.warning(f"Insufficient data for {symbol}")
                    continue

                # Calculate biases
                d1_bias = self.calculate_daily_bias(d1_data)
                h4_bias = self.h4_analyzer.calculate_bias(h4_data)

                logger.info(f"{symbol} - D1: {d1_bias}, H4: {h4_bias['bias']} ({h4_bias['confidence']}%)")

                # Skip if no clear D1 bias
                if d1_bias == "none":
                    continue

                # Find zones
                zones = self.zone_detector.find_zones(symbol, h1_data, d1_bias, h4_bias)

                # Send alert for BEST zone only (MAX 1 per symbol)
                if zones:
                    # Take only the best zone (highest R:R ratio)
                    best_zone = max(zones, key=lambda z: z.get('rr', 0))

                    # Validate price proximity before sending alert
                    current_price = self.data_fetcher.get_current_price(symbol)

                    if current_price is None:
                        logger.warning(f"Could not fetch current price for {symbol}, skipping alert")
                        continue

                    # Check if zone entry is within reasonable distance of current price
                    entry_price = best_zone["entry"]
                    price_distance = abs(current_price - entry_price)
                    max_distance = 0.01  # 100 pips for major pairs

                    if price_distance > max_distance:
                        logger.info(f"Zone filtered: {symbol} entry {entry_price:.5f} too far from current {current_price:.5f} (distance: {price_distance*10000:.1f} pips, max: {max_distance*10000:.0f} pips)")
                        continue

                    logger.info(f"Zone validated: {symbol} entry {entry_price:.5f} close to current {current_price:.5f} (distance: {price_distance*10000:.1f} pips)")

                    # Check zone freshness (formed within last 4 hours)
                    if hasattr(best_zone, 'formed_at') and best_zone.get('formed_at'):
                        from datetime import datetime, timedelta
                        zone_time = pd.to_datetime(best_zone['formed_at'])
                        current_time = datetime.now()
                        time_diff = current_time - zone_time.replace(tzinfo=None)

                        if time_diff > timedelta(hours=4):
                            logger.info(f"Zone too old for {symbol}: {time_diff}")
                            continue

                    bias_info = f"D1: {d1_bias.upper()} | H4: {h4_bias['bias'].upper()} ({h4_bias['confidence']}%)"

                    success = self.notifier.send_trading_alert(
                        symbol=symbol,
                        zone_type=best_zone["type"],
                        entry=best_zone["entry"],
                        stop=best_zone["stop"],
                        target=best_zone["target"],
                        rr=best_zone["rr"],
                        bias_info=bias_info,
                        current_price=current_price
                    )

                    if success:
                        # Record signal
                        self.tracker.record_signal(
                            symbol=symbol,
                            zone_type=best_zone["type"],
                            entry=best_zone["entry"],
                            stop=best_zone["stop"],
                            target=best_zone["target"],
                            rr=best_zone["rr"],
                            d1_bias=d1_bias,
                            h4_bias=h4_bias
                        )

                        signals_sent += 1
                        logger.info(f"Alert sent for {symbol} {best_zone['type']} zone (best of {len(zones)} zones)")

                # Small delay between symbols
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue

        # Increment scan count for next rotation
        self.scan_count += 1

        # Performance summary
        stats = self.tracker.get_performance_stats()
        logger.info(f"✅ Scan cycle complete. Signals sent: {signals_sent}")
        logger.info(f"📈 Performance: {stats}")

        return signals_sent

def main():
    """Main function for single scan"""
    bot = EnhancedTradingBot()
    return bot.run_scan()

def run_once():
    """Compatibility function for systemd"""
    try:
        result = main()
        logger.info(f"Scan completed successfully. Signals: {result}")
        return result
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        logger.error(traceback.format_exc())
        return 0

if __name__ == "__main__":
    run_once()