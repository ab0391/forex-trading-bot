#!/usr/bin/env python3
"""
TwelveData API Cache Manager
Reduces API calls by 50%+ through intelligent data caching
"""

import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd

class DataCacheManager:
    """Smart caching system to reduce TwelveData API calls"""

    def __init__(self, cache_dir: str = "/tmp/fxbot_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Cache validity periods (in minutes)
        self.cache_duration = {
            "1d": 60,   # 1 hour for daily data
            "4h": 30,   # 30 minutes for 4h data
            "1h": 15,   # 15 minutes for 1h data
            "price": 5  # 5 minutes for current price
        }

    def _get_cache_key(self, symbol: str, interval: str, outputsize: int) -> str:
        """Generate unique cache key"""
        data_string = f"{symbol}_{interval}_{outputsize}"
        return hashlib.md5(data_string.encode()).hexdigest()

    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.json"

    def is_cache_valid(self, cache_key: str, interval: str) -> bool:
        """Check if cached data is still valid"""
        cache_file = self._get_cache_file(cache_key)

        if not cache_file.exists():
            return False

        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            cache_duration_minutes = self.cache_duration.get(interval, 15)

            expires_at = cached_time + timedelta(minutes=cache_duration_minutes)
            return datetime.now() < expires_at

        except Exception:
            return False

    def get_cached_data(self, symbol: str, interval: str, outputsize: int) -> Optional[pd.DataFrame]:
        """Retrieve cached data if valid"""
        cache_key = self._get_cache_key(symbol, interval, outputsize)

        if not self.is_cache_valid(cache_key, interval):
            return None

        try:
            cache_file = self._get_cache_file(cache_key)
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Convert back to DataFrame
            df = pd.DataFrame(cache_data['data'])
            df['datetime'] = pd.to_datetime(df['datetime'])

            print(f"🎯 Cache HIT: {symbol} {interval} (saved API call)")
            return df

        except Exception as e:
            print(f"⚠️  Cache read error: {e}")
            return None

    def save_to_cache(self, data: pd.DataFrame, symbol: str, interval: str, outputsize: int):
        """Save data to cache"""
        cache_key = self._get_cache_key(symbol, interval, outputsize)
        cache_file = self._get_cache_file(cache_key)

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'data': data.to_dict('records')
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            print(f"💾 Cached: {symbol} {interval} for {self.cache_duration.get(interval, 15)}min")

        except Exception as e:
            print(f"⚠️  Cache save error: {e}")

    def get_cached_price(self, symbol: str) -> Optional[float]:
        """Get cached current price"""
        cache_key = self._get_cache_key(symbol, "price", 1)

        if not self.is_cache_valid(cache_key, "price"):
            return None

        try:
            cache_file = self._get_cache_file(cache_key)
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            print(f"🎯 Price Cache HIT: {symbol} = {cache_data['price']}")
            return cache_data['price']

        except Exception:
            return None

    def save_price_to_cache(self, symbol: str, price: float):
        """Save current price to cache"""
        cache_key = self._get_cache_key(symbol, "price", 1)
        cache_file = self._get_cache_file(cache_key)

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'price': price
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            print(f"💾 Price Cached: {symbol} = {price}")

        except Exception as e:
            print(f"⚠️  Price cache save error: {e}")

    def clear_expired_cache(self):
        """Clean up expired cache files"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)

                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cached_time > timedelta(hours=4):
                        cache_file.unlink()
                        print(f"🧹 Cleaned expired cache: {cache_file.name}")

                except Exception:
                    cache_file.unlink()  # Remove corrupted cache files

        except Exception as e:
            print(f"⚠️  Cache cleanup error: {e}")

# Global cache instance
cache_manager = DataCacheManager()
