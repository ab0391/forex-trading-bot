#!/usr/bin/env python3
"""
News Blackout System for ZoneSync FX Bot
Prevents trading during high-impact news events
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class NewsBlackoutSystem:
    """Monitors economic calendar and implements trading blackouts"""

    def __init__(self):
        # ForexFactory API alternative - using a simple calendar service
        self.calendar_api = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        self.blackout_cache_file = Path("/home/ubuntu/fxbot/news_blackout_cache.json")
        self.load_blackout_cache()

        # High impact news categories to avoid
        self.critical_events = [
            "Interest Rate Decision",
            "NFP", "Non-Farm Payrolls", "Employment",
            "GDP", "Gross Domestic Product",
            "CPI", "Consumer Price Index", "Inflation",
            "FOMC", "Federal Reserve", "Central Bank",
            "Retail Sales",
            "Industrial Production",
            "PMI", "Manufacturing",
            "Consumer Confidence"
        ]

        # Currency pairs to monitor
        self.monitored_currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CHF", "CAD"]

        # Blackout periods (minutes before and after news)
        self.blackout_before = 30  # 30 minutes before
        self.blackout_after = 60   # 60 minutes after

    def load_blackout_cache(self):
        """Load cached news events"""
        try:
            if self.blackout_cache_file.exists():
                with open(self.blackout_cache_file, 'r') as f:
                    self.blackout_cache = json.load(f)
            else:
                self.blackout_cache = {"last_update": None, "events": []}
        except Exception as e:
            logger.error(f"Error loading blackout cache: {e}")
            self.blackout_cache = {"last_update": None, "events": []}

    def save_blackout_cache(self):
        """Save news events to cache"""
        try:
            with open(self.blackout_cache_file, 'w') as f:
                json.dump(self.blackout_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving blackout cache: {e}")

    def fetch_news_events(self) -> List[Dict[str, Any]]:
        """Fetch upcoming news events from economic calendar"""

        try:
            # Check if cache is recent (within 6 hours)
            if self.blackout_cache.get("last_update"):
                last_update = datetime.fromisoformat(self.blackout_cache["last_update"])
                if datetime.now() - last_update < timedelta(hours=6):
                    logger.info("Using cached news events")
                    return self.blackout_cache.get("events", [])

            logger.info("Fetching fresh news events from calendar...")

            # Fetch from economic calendar API
            response = requests.get(self.calendar_api, timeout=10)
            response.raise_for_status()

            calendar_data = response.json()

            # Process events
            processed_events = []
            current_time = datetime.now()

            for event in calendar_data:
                try:
                    # Parse event data (format depends on API)
                    event_time = self._parse_event_time(event)

                    if not event_time or event_time < current_time:
                        continue  # Skip past events

                    # Check if it's within next 7 days
                    if event_time > current_time + timedelta(days=7):
                        continue

                    # Check if it's a critical event
                    if self._is_critical_event(event):
                        processed_event = {
                            "title": event.get("title", ""),
                            "currency": event.get("country", ""),
                            "impact": event.get("impact", ""),
                            "datetime": event_time.isoformat(),
                            "blackout_start": (event_time - timedelta(minutes=self.blackout_before)).isoformat(),
                            "blackout_end": (event_time + timedelta(minutes=self.blackout_after)).isoformat()
                        }
                        processed_events.append(processed_event)

                except Exception as e:
                    logger.warning(f"Error processing event: {e}")
                    continue

            # Update cache
            self.blackout_cache = {
                "last_update": datetime.now().isoformat(),
                "events": processed_events
            }
            self.save_blackout_cache()

            logger.info(f"Fetched {len(processed_events)} critical news events")
            return processed_events

        except Exception as e:
            logger.error(f"Error fetching news events: {e}")
            # Return cached events if fetch fails
            return self.blackout_cache.get("events", [])

    def _parse_event_time(self, event: Dict[str, Any]) -> Optional[datetime]:
        """Parse event datetime from API response"""
        try:
            # Different APIs have different datetime formats
            date_str = event.get("date", "")
            time_str = event.get("time", "")

            if not date_str:
                return None

            # Try different parsing approaches
            try:
                # Format: "2025-09-18" + "14:30"
                if time_str:
                    datetime_str = f"{date_str} {time_str}"
                    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                else:
                    return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                # Try ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

        except Exception as e:
            logger.warning(f"Error parsing event time: {e}")
            return None

    def _is_critical_event(self, event: Dict[str, Any]) -> bool:
        """Check if event is critical enough for blackout"""

        title = event.get("title", "").lower()
        impact = event.get("impact", "").lower()
        currency = event.get("country", "").upper()

        # Check impact level
        if impact in ["high", "red", "3"]:
            return True

        # Check currency relevance
        if currency not in self.monitored_currencies:
            return False

        # Check if title contains critical keywords
        for keyword in self.critical_events:
            if keyword.lower() in title:
                return True

        return False

    def is_blackout_period(self, symbol: str = None) -> Tuple[bool, Optional[str]]:
        """
        Check if current time is in a news blackout period

        Returns:
            (is_blackout, reason)
        """

        current_time = datetime.now()

        # Get current events
        events = self.fetch_news_events()

        for event in events:
            try:
                blackout_start = datetime.fromisoformat(event["blackout_start"])
                blackout_end = datetime.fromisoformat(event["blackout_end"])

                if blackout_start <= current_time <= blackout_end:
                    # Check if event affects the specific symbol
                    if symbol:
                        event_currency = event.get("currency", "").upper()
                        symbol_currencies = [symbol[:3], symbol[3:6]] if len(symbol) == 6 else [symbol[:3], symbol[4:7]]

                        if event_currency not in symbol_currencies:
                            continue  # Event doesn't affect this symbol

                    reason = f"News blackout: {event['title']} ({event['currency']}) at {event['datetime'][:16]}"
                    return True, reason

            except Exception as e:
                logger.warning(f"Error checking blackout period: {e}")
                continue

        return False, None

    def get_upcoming_blackouts(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming blackout periods"""

        current_time = datetime.now()
        cutoff_time = current_time + timedelta(hours=hours_ahead)

        events = self.fetch_news_events()
        upcoming = []

        for event in events:
            try:
                event_time = datetime.fromisoformat(event["datetime"])

                if current_time <= event_time <= cutoff_time:
                    upcoming.append({
                        "title": event["title"],
                        "currency": event["currency"],
                        "datetime": event["datetime"],
                        "hours_from_now": round((event_time - current_time).total_seconds() / 3600, 1)
                    })

            except Exception as e:
                logger.warning(f"Error processing upcoming event: {e}")
                continue

        return sorted(upcoming, key=lambda x: x["hours_from_now"])

    def create_simple_blackout_schedule(self) -> Dict[str, List[str]]:
        """
        Create a simple time-based blackout schedule as fallback
        All times in UTC
        """

        schedule = {
            "monday": ["08:30-09:30", "13:30-14:30"],     # European/US session overlap
            "tuesday": ["08:30-09:30", "13:30-14:30"],
            "wednesday": ["08:30-09:30", "13:30-14:30"],
            "thursday": ["08:30-09:30", "13:30-14:30"],
            "friday": ["08:30-09:30", "13:00-15:00"],     # NFP Friday
            "saturday": [],
            "sunday": []
        }

        return schedule

    def is_simple_blackout_time(self) -> Tuple[bool, Optional[str]]:
        """Check simple time-based blackout (fallback)"""

        current_time = datetime.now()
        weekday = current_time.strftime("%A").lower()
        current_hour_min = current_time.strftime("%H:%M")

        schedule = self.create_simple_blackout_schedule()
        blackout_periods = schedule.get(weekday, [])

        for period in blackout_periods:
            start_time, end_time = period.split("-")

            if start_time <= current_hour_min <= end_time:
                return True, f"Time-based blackout: {weekday} {period} UTC"

        return False, None

    def should_skip_trading(self, symbol: str = None) -> Tuple[bool, str]:
        """
        Main function to check if trading should be skipped

        Returns:
            (should_skip, reason)
        """

        # Check news-based blackout first
        is_news_blackout, news_reason = self.is_blackout_period(symbol)
        if is_news_blackout:
            return True, news_reason

        # Check time-based blackout as fallback
        is_time_blackout, time_reason = self.is_simple_blackout_time()
        if is_time_blackout:
            return True, time_reason

        return False, "No blackout active"

# Global instance
news_blackout = NewsBlackoutSystem()

def is_blackout_period(symbol: str = None) -> Tuple[bool, Optional[str]]:
    """Convenience function"""
    return news_blackout.is_blackout_period(symbol)

def should_skip_trading(symbol: str = None) -> Tuple[bool, str]:
    """Convenience function"""
    return news_blackout.should_skip_trading(symbol)

if __name__ == "__main__":
    # Test the news blackout system
    logging.basicConfig(level=logging.INFO)

    print("Testing News Blackout System...")

    # Test current blackout status
    skip_trading, reason = should_skip_trading("EURUSD")
    print(f"Should skip trading: {skip_trading}")
    if skip_trading:
        print(f"Reason: {reason}")

    # Test upcoming blackouts
    upcoming = news_blackout.get_upcoming_blackouts(24)
    print(f"\nUpcoming blackouts (next 24h): {len(upcoming)}")

    for event in upcoming[:5]:  # Show first 5
        print(f"- {event['title']} ({event['currency']}) in {event['hours_from_now']}h")

    print("\nNews blackout system test completed.")