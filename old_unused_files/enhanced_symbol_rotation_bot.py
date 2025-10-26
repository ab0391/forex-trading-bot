#!/usr/bin/env python3
"""
Enhanced Trading Bot with Symbol Rotation
- Maintains all 5 symbols but rotates through them
- 2 symbols per cycle to stay under API limits
- Full coverage across multiple scan cycles
"""

# Add this enhancement to the TradingBot class
class TradingBot:
    def __init__(self):
        # ... existing initialization code ...
        
        # Enhanced symbol management
        self.all_symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]
        self.symbols_per_cycle = 2  # Maximum symbols per scan to stay under API limit
        self.scan_count = 0
        self.shutdown_requested = False
    
    def get_symbols_for_current_scan(self):
        """Get symbols for current scan cycle with rotation"""
        start_idx = (self.scan_count * self.symbols_per_cycle) % len(self.all_symbols)
        end_idx = min(start_idx + self.symbols_per_cycle, len(self.all_symbols))
        
        symbols = self.all_symbols[start_idx:end_idx]
        
        # If we reach the end and don't have enough symbols, wrap around
        if len(symbols) < self.symbols_per_cycle and start_idx + self.symbols_per_cycle > len(self.all_symbols):
            remaining_needed = self.symbols_per_cycle - len(symbols)
            symbols.extend(self.all_symbols[:remaining_needed])
        
        logger.info(f"📊 Scan cycle {self.scan_count + 1}: Processing symbols {symbols}")
        return symbols
    
    def run_scan(self):
        """Enhanced run_scan with symbol rotation"""
        logger.info("🚀 Starting SYMBOL-ROTATED trading scan...")
        
        # Get symbols for this scan cycle
        current_symbols = self.get_symbols_for_current_scan()
        
        # Clean expired cache files
        cache_manager.clear_expired_cache()
        
        signals_sent = 0
        api_calls_made = 0
        
        for symbol in current_symbols:
            if self.shutdown_requested:
                break
            
            try:
                logger.info(f"Scanning {symbol}...")
                
                # Fetch data (4 API calls per symbol)
                d1_data = self.data_fetcher.fetch_data(symbol, "1d")
                h4_data = self.data_fetcher.fetch_data(symbol, "4h") 
                h1_data = self.data_fetcher.fetch_data(symbol, "1h")
                
                if not all([d1_data is not None, h4_data is not None, h1_data is not None]):
                    logger.warning(f"Insufficient data for {symbol}")
                    continue
                
                # ... rest of analysis logic remains the same ...
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        # Increment scan count for next rotation
        self.scan_count += 1
        
        # Log rotation status
        total_cycles_for_all_symbols = (len(self.all_symbols) + self.symbols_per_cycle - 1) // self.symbols_per_cycle
        cycle_in_rotation = (self.scan_count - 1) % total_cycles_for_all_symbols + 1
        
        logger.info(f"✅ Scan complete. Rotation: {cycle_in_rotation}/{total_cycles_for_all_symbols} (All symbols covered every {total_cycles_for_all_symbols} cycles)")
        
        return signals_sent

# Usage example:
# Cycle 1: ["EUR/USD", "GBP/USD"] → 8 API calls
# Cycle 2: ["USD/JPY", "AUD/USD"] → 8 API calls  
# Cycle 3: ["USD/CHF", "EUR/USD"] → 8 API calls (wraps around)
# Result: All 5 symbols covered across 3 cycles, never exceeding 8 calls/cycle
