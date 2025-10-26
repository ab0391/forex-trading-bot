#!/usr/bin/env python3
"""
TwelveData Rate Limiter
Ensures API calls stay under 8 per minute limit
"""

import time
import threading
from collections import deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TwelveDataRateLimiter:
    """
    Rate limiter for TwelveData API
    - Max 8 calls per minute (actually 7 for safety margin)
    - Distributes calls evenly across the minute
    - Thread-safe implementation
    """
    
    def __init__(self, max_calls_per_minute=7):
        self.max_calls = max_calls_per_minute
        self.call_times = deque()
        self.lock = threading.Lock()
        
        # Calculate minimum time between calls
        self.min_interval = 60.0 / max_calls_per_minute  # ~8.57 seconds for 7 calls/minute
        self.last_call_time = 0
        
        logger.info(f"🛡️  Rate limiter initialized: max {max_calls_per_minute} calls/minute")
        logger.info(f"⏰ Minimum interval between calls: {self.min_interval:.1f} seconds")
    
    def wait_if_needed(self):
        """
        Wait if necessary to respect rate limits
        Call this before making any API request
        """
        with self.lock:
            current_time = time.time()
            
            # Remove old call times (older than 1 minute)
            cutoff_time = current_time - 60
            while self.call_times and self.call_times[0] < cutoff_time:
                self.call_times.popleft()
            
            # Check if we need to wait based on call count
            if len(self.call_times) >= self.max_calls:
                # We've made max calls in the last minute
                oldest_call = self.call_times[0]
                wait_time = 60 - (current_time - oldest_call)
                if wait_time > 0:
                    logger.info(f"⏳ Rate limit reached. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    # Remove the old call after waiting
                    if self.call_times:
                        self.call_times.popleft()
            
            # Check minimum interval between calls
            time_since_last = current_time - self.last_call_time
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                logger.info(f"⏱️  Enforcing minimum interval. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                current_time = time.time()
            
            # Record this call
            self.call_times.append(current_time)
            self.last_call_time = current_time
            
            logger.info(f"🟢 API call allowed. Recent calls: {len(self.call_times)}/{self.max_calls}")
    
    def get_status(self):
        """Get current rate limiter status"""
        with self.lock:
            current_time = time.time()
            
            # Clean old calls
            cutoff_time = current_time - 60
            while self.call_times and self.call_times[0] < cutoff_time:
                self.call_times.popleft()
            
            calls_in_last_minute = len(self.call_times)
            time_since_last = current_time - self.last_call_time if self.last_call_time else float('inf')
            
            return {
                'calls_in_last_minute': calls_in_last_minute,
                'max_calls_per_minute': self.max_calls,
                'time_since_last_call': time_since_last,
                'min_interval': self.min_interval,
                'can_make_call_now': calls_in_last_minute < self.max_calls and time_since_last >= self.min_interval
            }

# Global rate limiter instance
twelvedata_rate_limiter = TwelveDataRateLimiter()

class EnhancedRateLimiter:
    """
    Enhanced rate limiter with adaptive timing
    Prevents bursts and ensures smooth distribution
    """
    
    def __init__(self):
        self.twelvedata_limiter = twelvedata_rate_limiter
        self.call_count = 0
        self.session_start = time.time()
    
    def wait_for_api_call(self, api_type="TwelveData"):
        """
        Wait appropriately before making an API call
        """
        if api_type == "TwelveData":
            self.twelvedata_limiter.wait_if_needed()
            self.call_count += 1
            
            # Log session statistics
            if self.call_count % 5 == 0:
                session_duration = time.time() - self.session_start
                rate = self.call_count / (session_duration / 60) if session_duration > 0 else 0
                logger.info(f"📊 Session stats: {self.call_count} calls in {session_duration/60:.1f}min (rate: {rate:.1f}/min)")
        else:
            # For other APIs (Yahoo Finance, etc.) - no limit needed
            logger.debug(f"🚀 {api_type} call (no rate limit)")
    
    def get_comprehensive_status(self):
        """Get detailed status information"""
        td_status = self.twelvedata_limiter.get_status()
        session_duration = time.time() - self.session_start
        
        return {
            'session_calls': self.call_count,
            'session_duration_minutes': session_duration / 60,
            'session_rate': self.call_count / (session_duration / 60) if session_duration > 0 else 0,
            'twelvedata_status': td_status
        }

# Global enhanced rate limiter
enhanced_rate_limiter = EnhancedRateLimiter()
