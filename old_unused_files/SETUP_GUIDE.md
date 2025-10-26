# Trading Bot - Quick Setup Guide

## ✅ Dashboard Status: **WORKING**

Your dashboard is now running at:
- **Local:** http://localhost:5000
- **Network:** http://84.235.245.60:5000

### Dashboard Features:
- View all trading signals in real-time
- Track performance metrics (win rate, P&L, etc.)
- Beautiful charts and visualizations
- Record trade outcomes (Win/Loss)

---

## ⚠️ Telegram Notifications: **NEEDS SETUP**

Your Telegram bot is not configured yet. Here's how to set it up:

### Step 1: Create a Telegram Bot

1. Open Telegram app
2. Search for `@BotFather`
3. Send the command: `/newbot`
4. Follow instructions:
   - Give your bot a name (e.g., "My Trading Bot")
   - Give it a username (e.g., "my_trading_signals_bot")
5. **BotFather will give you a TOKEN** - copy it!
   - It looks like: `123456789:ABCdefGhIJKlmnoPQRstuVWXyz`

### Step 2: Get Your Chat ID

1. Search for your bot on Telegram (the username you created)
2. Click "Start" or send any message to it
3. Open this URL in your browser (replace YOUR_TOKEN with your actual token):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":` followed by a number
5. That number is your CHAT_ID (e.g., `123456789`)

### Step 3: Update Your .env File

Edit the file: `/Users/andrewbuck/Desktop/Trading Bot/.env`

Replace these lines:
```
TELEGRAM_BOT_TOKEN=your_telegram_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

With your actual values:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmnoPQRstuVWXyz
TELEGRAM_CHAT_ID=123456789
```

### Step 4: Test Your Setup

Run this command:
```bash
cd "/Users/andrewbuck/Desktop/Trading Bot"
python3 test_telegram_simple.py
```

If successful, you'll receive a test message on Telegram!

---

## 🎯 What You'll Get

Once configured, your bot will send you:
- 📊 Trading signal alerts when opportunities are found
- 💰 Entry, stop loss, and target prices
- 📈 Risk/reward ratios
- 🎯 Market bias analysis
- ⏰ Real-time notifications

**No spam!** The bot has built-in spam prevention and only sends quality signals.

---

## 🚀 Quick Start

1. **Dashboard is already running!** Visit http://localhost:5000
2. Set up Telegram (follow steps above)
3. Test with: `python3 test_telegram_simple.py`
4. Start your trading bot (if not already running)

---

## 📝 Need Help?

- Dashboard not loading? Make sure port 5000 isn't blocked by firewall
- Can't access on network? Check your router settings for port forwarding
- Telegram not working? Double-check your token and chat ID

---

## 🛠️ Useful Commands

**Check if dashboard is running:**
```bash
curl http://localhost:5000/api/health
```

**View dashboard logs:**
```bash
tail -f /tmp/enhanced_bot.log
```

**Restart dashboard:**
```bash
pkill -f dashboard_server_mac.py
python3 dashboard_server_mac.py &
```

---

**Current Status:**
- ✅ Dashboard: Running on port 5000
- ⚠️  Telegram: Needs configuration
- 📅 Date: October 10, 2025

