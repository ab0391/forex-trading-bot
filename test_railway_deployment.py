#!/usr/bin/env python3
"""
Test Railway Deployment
Verifies that all components are working correctly
"""

import os
import sys
import json
import requests
from datetime import datetime
import pytz

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        from trade_tracker import TradeTracker
        print("✅ TradeTracker imported successfully")
    except ImportError as e:
        print(f"❌ TradeTracker import failed: {e}")
        return False
    
    try:
        from dynamic_rr_optimizer import DynamicRROptimizer
        print("✅ DynamicRROptimizer imported successfully")
    except ImportError as e:
        print(f"❌ DynamicRROptimizer import failed: {e}")
        return False
    
    try:
        from daily_summary_system import DailySummarySystem
        print("✅ DailySummarySystem imported successfully")
    except ImportError as e:
        print(f"❌ DailySummarySystem import failed: {e}")
        return False
    
    return True

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = [
        'FOREX_TELEGRAM_BOT_TOKEN',
        'FOREX_TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"❌ {var} not set")
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in Railway dashboard")
        return False
    
    return True

def test_telegram_connection():
    """Test Telegram bot connection"""
    print("\n🔍 Testing Telegram connection...")
    
    token = os.getenv('FOREX_TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('FOREX_TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Telegram credentials not available")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ Telegram bot connected: @{data['result']['username']}")
                return True
            else:
                print(f"❌ Telegram API error: {data}")
                return False
        else:
            print(f"❌ Telegram connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram connection error: {e}")
        return False

def test_yahoo_finance():
    """Test Yahoo Finance data access"""
    print("\n🔍 Testing Yahoo Finance...")
    
    try:
        import yfinance as yf
        ticker = yf.Ticker("EURUSD=X")
        data = ticker.history(period="1d")
        
        if not data.empty:
            print("✅ Yahoo Finance data access working")
            return True
        else:
            print("❌ Yahoo Finance returned empty data")
            return False
    except Exception as e:
        print(f"❌ Yahoo Finance error: {e}")
        return False

def test_file_structure():
    """Test if required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'yahoo_forex_bot.py',
        'enhanced_orb_stock_bot.py',
        'dashboard_server_mac.py',
        'trade_tracker.py',
        'dynamic_rr_optimizer.py',
        'daily_summary_system.py',
        'config.py',
        'Procfile',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_bot_initialization():
    """Test if bots can be initialized"""
    print("\n🔍 Testing bot initialization...")
    
    try:
        from yahoo_forex_bot import YahooTradingBot
        bot = YahooTradingBot()
        print("✅ Forex bot initialized successfully")
    except Exception as e:
        print(f"❌ Forex bot initialization failed: {e}")
        return False
    
    try:
        from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
        stock_bot = EnhancedORBStockTradingBot()
        print("✅ Stock bot initialized successfully")
    except Exception as e:
        print(f"❌ Stock bot initialization failed: {e}")
        return False
    
    return True

def test_daily_summary():
    """Test daily summary system"""
    print("\n🔍 Testing daily summary system...")
    
    try:
        from daily_summary_system import DailySummarySystem
        from config import FOREX_TELEGRAM_BOT_TOKEN, FOREX_TELEGRAM_CHAT_ID
        
        summary_system = DailySummarySystem(FOREX_TELEGRAM_BOT_TOKEN, FOREX_TELEGRAM_CHAT_ID)
        
        # Test forex summary generation
        forex_summary = summary_system.get_forex_daily_summary()
        if forex_summary and "FOREX BOT DAILY SUMMARY" in forex_summary:
            print("✅ Forex daily summary generation working")
        else:
            print("❌ Forex daily summary generation failed")
            return False
        
        # Test UK summary generation
        uk_summary = summary_system.get_stock_uk_market_close_summary()
        if uk_summary and "UK STOCK MARKET CLOSE" in uk_summary:
            print("✅ UK market close summary generation working")
        else:
            print("❌ UK market close summary generation failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Daily summary system error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Railway Deployment Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Telegram Connection", test_telegram_connection),
        ("Yahoo Finance", test_yahoo_finance),
        ("File Structure", test_file_structure),
        ("Bot Initialization", test_bot_initialization),
        ("Daily Summary", test_daily_summary)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Railway deployment should work.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    # Show current time in Dubai
    dubai_tz = pytz.timezone('Asia/Dubai')
    dubai_time = datetime.now(dubai_tz)
    print(f"\n🕐 Current Dubai time: {dubai_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)