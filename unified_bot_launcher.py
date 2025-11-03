#!/usr/bin/env python3
"""
Unified Bot Launcher - Runs both Forex and Stock bots simultaneously
Required for Railway free tier (only runs 1 worker process)
"""

import threading
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_forex_bot():
    """Run the forex trading bot"""
    try:
        logger.info("🚀 Starting Forex Bot...")
        from yahoo_forex_bot import main as forex_main
        forex_main()
    except Exception as e:
        logger.error(f"❌ Forex bot error: {e}")
        import traceback
        traceback.print_exc()

def run_stock_bot():
    """Run the stock trading bot"""
    try:
        logger.info("🚀 Starting Stock Bot...")
        from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
        bot = EnhancedORBStockTradingBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Stock bot error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Launch both bots in parallel using threads (Railway compatible)"""
    logger.info("=" * 70)
    logger.info("🚀 UNIFIED BOT LAUNCHER - Starting Both Bots")
    logger.info("=" * 70)
    
    # Use threads instead of processes (more Railway-compatible)
    forex_thread = threading.Thread(target=run_forex_bot, name="ForexBot", daemon=True)
    stock_thread = threading.Thread(target=run_stock_bot, name="StockBot", daemon=True)
    
    # Start both threads
    logger.info("🟢 Starting Forex Bot thread...")
    forex_thread.start()
    
    time.sleep(2)  # Small delay between starts
    
    logger.info("🟢 Starting Stock Bot thread...")
    stock_thread.start()
    
    logger.info("=" * 70)
    logger.info("✅ Both bots launched successfully!")
    logger.info("=" * 70)
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(60)
            if not forex_thread.is_alive():
                logger.error("❌ Forex bot thread died!")
            if not stock_thread.is_alive():
                logger.error("❌ Stock bot thread died!")
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown signal received")
        logger.info("✅ Bots will stop gracefully")

if __name__ == "__main__":
    main()
