#!/usr/bin/env python3
"""
Railway Deployment Helper Script
"""

import subprocess
import os
import webbrowser

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Railway Deployment Helper")
    print("=" * 40)
    
    print("\n📋 Deployment Checklist:")
    print("1. ✅ GitHub repositories created")
    print("2. ✅ Trading bots implemented")
    print("3. ✅ Telegram credentials configured")
    print("4. ⏳ Ready for Railway deployment")
    
    print("\n🔗 GitHub Repositories:")
    print("• Forex Bot: https://github.com/ab0391/forex-trading-bot")
    print("• Stock Bot: https://github.com/ab0391/stock-trading-bot")
    
    print("\n📱 Telegram Bots:")
    print("• Forex: @fx_pairs_bot")
    print("• Stock: @breakout_trading_bot")
    
    print("\n🎯 Next Steps:")
    print("1. Go to railway.app")
    print("2. Sign up with GitHub account")
    print("3. Deploy both repositories")
    print("4. Add environment variables")
    print("5. Start 24/7 trading!")
    
    # Check if Railway CLI is installed
    print("\n🔧 Checking Railway CLI...")
    success, stdout, stderr = run_command("railway --version")
    
    if success:
        print("✅ Railway CLI is installed")
        print("💡 You can also deploy via CLI if preferred")
    else:
        print("ℹ️ Railway CLI not installed (optional)")
        print("💡 You can deploy via web interface at railway.app")
    
    # Open Railway in browser
    print("\n🌐 Opening Railway in browser...")
    try:
        webbrowser.open("https://railway.app")
        print("✅ Railway opened in browser")
    except Exception as e:
        print(f"⚠️ Could not open browser: {e}")
        print("💡 Please go to https://railway.app manually")
    
    print("\n📖 For detailed instructions, see:")
    print("• COMPLETE_RAILWAY_DEPLOYMENT_GUIDE.md")
    
    print("\n🎉 Ready to deploy your 24/7 trading empire!")

if __name__ == "__main__":
    main()
