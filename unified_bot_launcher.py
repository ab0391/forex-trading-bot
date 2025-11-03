#!/usr/bin/env python3
"""
Unified Bot Launcher - Runs both Forex and Stock bots simultaneously
Required for Railway free tier (only runs 1 worker process)
"""

import multiprocessing
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
        sys.exit(1)

def run_stock_bot():
    """Run the stock trading bot"""
    try:
        logger.info("🚀 Starting Stock Bot...")
        from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
        bot = EnhancedORBStockTradingBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Stock bot error: {e}")
        sys.exit(1)

def main():
    """Launch both bots in parallel"""
    logger.info("=" * 70)
    logger.info("🚀 UNIFIED BOT LAUNCHER - Starting Both Bots")
    logger.info("=" * 70)
    
    # Create processes for both bots
    forex_process = multiprocessing.Process(target=run_forex_bot, name="ForexBot")
    stock_process = multiprocessing.Process(target=run_stock_bot, name="StockBot")
    
    # Start both processes
    logger.info("🟢 Starting Forex Bot process...")
    forex_process.start()
    
    time.sleep(2)  # Small delay between starts
    
    logger.info("🟢 Starting Stock Bot process...")
    stock_process.start()
    
    logger.info("=" * 70)
    logger.info("✅ Both bots launched successfully!")
    logger.info(f"   Forex Bot PID: {forex_process.pid}")
    logger.info(f"   Stock Bot PID: {stock_process.pid}")
    logger.info("=" * 70)
    
    try:
        # Monitor both processes
        while True:
            if not forex_process.is_alive():
                logger.error("❌ Forex bot stopped! Restarting...")
                forex_process = multiprocessing.Process(target=run_forex_bot, name="ForexBot")
                forex_process.start()
            
            if not stock_process.is_alive():
                logger.error("❌ Stock bot stopped! Restarting...")
                stock_process = multiprocessing.Process(target=run_stock_bot, name="StockBot")
                stock_process.start()
            
            time.sleep(60)  # Check every minute
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown signal received")
        forex_process.terminate()
        stock_process.terminate()
        forex_process.join(timeout=5)
        stock_process.join(timeout=5)
        logger.info("✅ Both bots stopped cleanly")

if __name__ == "__main__":
    main()
