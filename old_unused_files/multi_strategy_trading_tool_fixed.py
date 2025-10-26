#!/usr/bin/env python3
"""
ZoneSync FX Bot - Enhanced with comprehensive error handling and stability fixes
"""

import os
import time
import logging
import traceback
import signal
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup robust logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/fxbot/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotStabilityManager:
    """Manages bot stability, error recovery, and graceful shutdown"""

    def __init__(self):
        self.consecutive_failures = 0
        self.max_failures = 5
        self.shutdown_requested = False
        self.session = self._create_robust_session()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True

    def _create_robust_session(self):
        """Create HTTP session with connection pooling and retry logic"""
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def run_with_stability(self, main_func):
        """Run main function with comprehensive error handling"""
        logger.info("ZoneSync FX Bot starting with enhanced stability...")

        while not self.shutdown_requested:
            cycle_start = time.time()

            try:
                # Run main trading logic
                main_func()

                # Reset failure counter on success
                self.consecutive_failures = 0
                logger.info("Trading cycle completed successfully")

            except KeyboardInterrupt:
                logger.info("Shutdown requested by user")
                break

            except Exception as e:
                self.consecutive_failures += 1
                error_msg = f"Trading cycle failed (attempt {self.consecutive_failures}): {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())

                # Implement progressive backoff strategy
                if self.consecutive_failures >= self.max_failures:
                    logger.critical(f"Too many consecutive failures ({self.consecutive_failures}), entering extended sleep")
                    sleep_duration = 3600 * 6  # 6 hours
                    self.consecutive_failures = 0  # Reset after long sleep
                else:
                    # Progressive backoff: 5min, 10min, 15min, 20min, 25min
                    sleep_duration = min(300 * self.consecutive_failures, 1500)
                    logger.warning(f"Sleeping {sleep_duration}s before retry")

                # Sleep with interruption checking
                self._interruptible_sleep(sleep_duration)
                continue

            # Calculate how long the cycle took
            cycle_duration = time.time() - cycle_start

            # Sleep for remainder of hour, checking for shutdown
            remaining_sleep = max(0, 3600 - cycle_duration)
            logger.info(f"Cycle took {cycle_duration:.1f}s, sleeping {remaining_sleep:.1f}s")

            if remaining_sleep > 0:
                self._interruptible_sleep(remaining_sleep)

        logger.info("ZoneSync FX Bot shutdown complete")

    def _interruptible_sleep(self, duration):
        """Sleep that can be interrupted by shutdown signal"""
        end_time = time.time() + duration

        while time.time() < end_time and not self.shutdown_requested:
            time.sleep(min(1, end_time - time.time()))


class RobustDataFetcher:
    """Enhanced data fetcher with connection pooling and error handling"""

    def __init__(self, session: requests.Session):
        self.session = session
        self.td_key = os.getenv("TWELVEDATA_API_KEY")
        self.rate_limit_sleep = 65
        self.daily_limit_reached = False

    def fetch_twelvedata(self, symbol: str, interval: str,
                        start: Optional[str] = None, end: Optional[str] = None,
                        outputsize: int = 5000) -> Optional[pd.DataFrame]:
        """Fetch data from TwelveData with robust error handling"""

        if not self.td_key:
            logger.error("TWELVEDATA_API_KEY missing in environment")
            return None

        if self.daily_limit_reached:
            logger.info("Daily limit reached, skipping TwelveData call")
            return None

        params = {
            "symbol": symbol,
            "interval": self._convert_interval(interval),
            "apikey": self.td_key,
            "outputsize": outputsize,
            "timezone": "UTC",
            "format": "JSON",
            "order": "ASC",
        }

        if start:
            params["start_date"] = start
        if end:
            params["end_date"] = end

        url = "https://api.twelvedata.com/time_series"

        try:
            logger.debug(f"Fetching {symbol} data from TwelveData...")

            response = self.session.get(
                url,
                params=params,
                timeout=(10, 30)  # 10s connect, 30s read timeout
            )
            response.raise_for_status()

            data = response.json()

            # Handle API errors
            if "values" not in data:
                error_msg = data.get("message", str(data))

                # Check for rate limiting
                if "API credits" in error_msg or "limit" in error_msg.lower():
                    logger.warning(f"TwelveData rate limit hit: {error_msg}")
                    if "daily" in error_msg.lower():
                        self.daily_limit_reached = True
                    time.sleep(self.rate_limit_sleep)
                    return None

                logger.error(f"TwelveData API error for {symbol}: {error_msg}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(data["values"])
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            # Ensure proper data types
            df = self._ensure_dataframe_types(df)
            logger.debug(f"Successfully fetched {len(df)} rows for {symbol}")
            return df

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching data for {symbol}")
            return None

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching data for {symbol}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching {symbol}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol}: {e}")
            return None

    def _convert_interval(self, interval: str) -> str:
        """Convert interval to TwelveData format"""
        interval_map = {
            "1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min",
            "1h": "1h", "4h": "4h", "1d": "1day", "1w": "1week"
        }
        return interval_map.get(interval, interval)

    def _ensure_dataframe_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure DataFrame has correct data types"""
        if df.empty:
            return df

        # Convert datetime
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])

        # Convert OHLCV to numeric
        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df


def main():
    """Main trading logic - placeholder for your existing code"""
    logger.info("Running main trading cycle...")

    # This is where your existing trading logic would go
    # For now, just a placeholder that simulates work

    stability_manager = BotStabilityManager()
    data_fetcher = RobustDataFetcher(stability_manager.session)

    # Example: Fetch some data to test the system
    test_pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]

    for pair in test_pairs:
        logger.info(f"Processing {pair}...")

        # Simulate your trading logic here
        data = data_fetcher.fetch_twelvedata(pair, "1h", outputsize=100)

        if data is not None:
            logger.info(f"Successfully processed {pair}: {len(data)} candles")
        else:
            logger.warning(f"Failed to fetch data for {pair}")

        # Small delay between pairs
        time.sleep(2)

    logger.info("Main trading cycle completed")


if __name__ == "__main__":
    # Create stability manager and run bot
    stability_manager = BotStabilityManager()
    stability_manager.run_with_stability(main)