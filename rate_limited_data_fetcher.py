#!/usr/bin/env python3
"""
Rate-Limited Data Fetcher for Railway Deployment
Handles Yahoo Finance rate limiting with proper delays and retry logic
"""

import yfinance as yf
import pandas as pd
import time
import logging
import random
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class RateLimitedDataFetcher:
    """Data fetcher with built-in rate limiting for cloud deployment"""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 10.0):
        self.base_delay = base_delay  # Base delay between requests
        self.max_delay = max_delay    # Maximum delay for exponential backoff
        self.last_request_time = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        
        # Setup requests session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info("✅ Rate-Limited Data Fetcher initialized")
        logger.info(f"   Base delay: {base_delay}s, Max delay: {max_delay}s")
    
    def _wait_for_rate_limit(self):
        """Wait appropriate time between requests to avoid rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Calculate delay based on consecutive failures
        if self.consecutive_failures > 0:
            # Exponential backoff with jitter
            delay = min(self.base_delay * (2 ** self.consecutive_failures), self.max_delay)
            # Add random jitter to avoid thundering herd
            jitter = random.uniform(0.1, 0.5)
            delay += jitter
        else:
            delay = self.base_delay + random.uniform(0.1, 0.3)
        
        # Ensure minimum delay
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"⏳ Rate limiting: waiting {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price with rate limiting and retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                
                # Convert symbol to Yahoo Finance format
                yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
                
                logger.debug(f"🔍 Fetching price for {symbol} (attempt {attempt + 1})")
                
                ticker = yf.Ticker(yahoo_symbol)
                data = ticker.history(period="1d", interval="1m")
                
                if data.empty:
                    logger.warning(f"⚠️ No data for {symbol}")
                    self.consecutive_failures += 1
                    continue
                
                current_price = float(data['Close'].iloc[-1])
                logger.debug(f"✅ {symbol}: {current_price}")
                
                # Reset failure counter on success
                self.consecutive_failures = 0
                return current_price
                
            except Exception as e:
                self.consecutive_failures += 1
                logger.warning(f"⚠️ Error fetching {symbol} (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retry
                    wait_time = self.base_delay * (2 ** attempt)
                    logger.debug(f"⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to fetch {symbol} after {max_retries} attempts")
        
        return None
    
    def get_historical_data(self, symbol: str, period: str = "1mo", interval: str = "1h") -> Optional[pd.DataFrame]:
        """Get historical data with rate limiting"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                
                yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
                
                logger.debug(f"📊 Fetching historical data for {symbol} ({period}, {interval})")
                
                ticker = yf.Ticker(yahoo_symbol)
                data = ticker.history(period=period, interval=interval)
                
                if data.empty:
                    logger.warning(f"⚠️ No historical data for {symbol}")
                    self.consecutive_failures += 1
                    continue
                
                logger.debug(f"✅ {symbol}: {len(data)} candles")
                self.consecutive_failures = 0
                return data
                
            except Exception as e:
                self.consecutive_failures += 1
                logger.warning(f"⚠️ Error fetching historical data for {symbol}: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = self.base_delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to fetch historical data for {symbol}")
        
        return None
    
    def _convert_to_yahoo_symbol(self, symbol: str) -> str:
        """Convert trading symbol to Yahoo Finance format"""
        # Forex pairs
        if "/" in symbol:
            return f"{symbol}=X"
        
        # Crypto
        crypto_map = {
            "BITCOIN": "BTC-USD",
            "ETHEREUM": "ETH-USD"
        }
        if symbol in crypto_map:
            return crypto_map[symbol]
        
        # Commodities
        commodity_map = {
            "GOLD": "GC=F",
            "SILVER": "SI=F",
            "OIL": "CL=F"
        }
        if symbol in commodity_map:
            return commodity_map[symbol]
        
        # Stocks (already in correct format)
        return symbol
    
    def get_multiple_prices(self, symbols: list, delay_between: float = 0.5) -> Dict[str, float]:
        """Get prices for multiple symbols with proper spacing"""
        prices = {}
        
        for i, symbol in enumerate(symbols):
            price = self.get_current_price(symbol)
            if price:
                prices[symbol] = price
            
            # Additional delay between symbols
            if i < len(symbols) - 1:
                time.sleep(delay_between)
        
        return prices
    
    def get_status(self) -> Dict[str, Any]:
        """Get fetcher status for monitoring"""
        return {
            "consecutive_failures": self.consecutive_failures,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "last_request_time": self.last_request_time
        }

def test_rate_limited_fetcher():
    """Test the rate-limited fetcher"""
    print("🧪 Testing Rate-Limited Data Fetcher...")
    
    fetcher = RateLimitedDataFetcher(base_delay=2.0)
    
    # Test symbols
    test_symbols = ["EUR/USD", "GBP/USD", "AAPL", "GOLD"]
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing {symbol}...")
        price = fetcher.get_current_price(symbol)
        if price:
            print(f"✅ {symbol}: {price}")
        else:
            print(f"❌ {symbol}: Failed")
    
    print(f"\n📊 Status: {fetcher.get_status()}")

if __name__ == "__main__":
    test_rate_limited_fetcher()
