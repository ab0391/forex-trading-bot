# Railway Deployment Fix Guide

## 🚨 Current Issue
The bots are only working when your laptop is on, which means Railway deployment is not working properly.

## 🔧 Step-by-Step Fix

### 1. Check Railway Dashboard
1. Go to https://railway.app/dashboard
2. Check if both projects are deployed:
   - `fxbot` (forex bot)
   - `stock-bot` (stock bot)

### 2. Check Deployment Logs
For each project, check the logs:
1. Click on the project
2. Go to "Deployments" tab
3. Click on the latest deployment
4. Check the logs for any errors

### 3. Common Issues & Fixes

#### Issue A: Environment Variables Missing
**Problem:** Bots can't find Telegram credentials
**Fix:** Add environment variables in Railway dashboard:
```
TELEGRAM_BOT_TOKEN=your_forex_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_TOKEN=your_stock_bot_token
ACCOUNT_SIZE=50000
RISK_PER_TRADE=0.01
```

#### Issue B: Dependencies Not Installing
**Problem:** Python packages not installing correctly
**Fix:** Check `requirements.txt` includes all dependencies:
```
yfinance>=0.2.18
pandas>=1.5.0
numpy>=1.26.0
requests>=2.28.0
python-dotenv>=0.19.0
pytz>=2022.1
```

#### Issue C: File Path Issues
**Problem:** Bots can't find files on Railway
**Fix:** Ensure all files are in the root directory

### 4. Test Deployment
1. Check if processes are running:
   - `web` process (dashboard)
   - `worker` process (forex bot)
   - `stock_worker` process (stock bot)

2. Check logs for:
   - "✅ Yahoo Finance loaded"
   - "✅ Trade Tracker loaded"
   - "✅ Daily Summary System loaded"
   - "🚀 Bot started"

### 5. Verify 24/7 Operation
1. Close your laptop
2. Wait 30 minutes
3. Check if you receive signals via Telegram
4. If no signals, check Railway logs

## 🎯 Expected Behavior After Fix

### Forex Bot (24/7)
- Scans every 15 minutes
- Sends signals via Telegram
- Sends daily summary at 9 PM Dubai
- Tracks trades and prevents duplicates

### Stock Bot (Market Hours)
- UK market: 11:30 AM - 4:30 PM Dubai
- US market: 4:30 PM - 1:00 AM Dubai
- Sends market close notifications
- Auto-closes positions at market close

## 📱 Telegram Notifications You Should Receive

### Forex Bot
- Real-time signal alerts
- Daily summary at 9 PM Dubai
- Trade closure notifications

### Stock Bot
- UK market close warning (4:15 PM Dubai)
- US market close warning (12:45 AM Dubai)
- Real-time signal alerts during market hours

## 🔍 Troubleshooting

### If No Signals Received
1. Check Railway logs for errors
2. Verify Telegram bot tokens are correct
3. Check if markets are open
4. Verify environment variables

### If Bots Keep Restarting
1. Check for Python errors in logs
2. Verify all dependencies are installed
3. Check file permissions

### If Dashboard Not Loading
1. Check `web` process is running
2. Verify dashboard server is accessible
3. Check for port conflicts

## 📞 Next Steps
1. Check Railway dashboard for both projects
2. Verify all environment variables are set
3. Check deployment logs for errors
4. Test by closing laptop for 30 minutes
5. Report back with any issues found

## 🎯 Success Criteria
- ✅ Bots run 24/7 without laptop
- ✅ Receive signals via Telegram
- ✅ Daily summaries at correct times
- ✅ Market close notifications
- ✅ No contradictory signals
