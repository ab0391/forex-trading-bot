# 🚀 Quick Reference Guide

## 📊 **Check Trade Status**

```bash
# Quick verification
python3 verify_trade_tracking.py

# See active trades
cat active_trades.json | python3 -m json.tool

# See cooldown trades
cat cooldown_trades.json | python3 -m json.tool

# See trade history
cat trade_history.json | python3 -m json.tool
```

---

## 🤖 **Bot Management**

```bash
# Check if bot is running
ps aux | grep yahoo_forex_bot

# Start the bot
python3 yahoo_forex_bot.py &

# Stop the bot
pkill -f yahoo_forex_bot

# Restart the bot
pkill -f yahoo_forex_bot && sleep 2 && python3 yahoo_forex_bot.py &
```

---

## 📱 **Dashboard Management**

```bash
# Check if dashboard is running
ps aux | grep dashboard_server_mac

# Start the dashboard
python3 dashboard_server_mac.py &

# Stop the dashboard
pkill -f dashboard_server_mac

# Restart the dashboard
pkill -f dashboard_server_mac && sleep 2 && python3 dashboard_server_mac.py &
```

---

## 🔍 **What Each File Does**

| File | What It Tracks |
|------|----------------|
| `active_trades.json` | Trades currently running (not hit stop/target yet) |
| `cooldown_trades.json` | Pairs that can't trade for 4 hours (recently closed) |
| `trade_history.json` | All completed trades (wins/losses) |
| `signals_history.json` | Raw signal data for dashboard |
| `trades_history.json` | Dashboard trade display data |

---

## 🎯 **How Trade Lifecycle Works**

```
1. Signal Generated → Added to active_trades.json
                    ↓
2. Every 15 minutes → Bot checks current price
                    ↓
3. Stop/Target Hit → Moved to trade_history.json
                    → Added to cooldown_trades.json
                    ↓
4. After 4 Hours → Removed from cooldown
                 → Pair can generate new signals
```

---

## 🚨 **What's Been Fixed**

### ✅ **No More Contradictory Signals**
**Before:**
- USD/CHF SHORT @ 19:38
- USD/CHF LONG @ 20:22 ❌ (trading against yourself!)

**After:**
- USD/CHF SHORT @ 19:38
- USD/CHF blocked until trade closes + 4 hours ✅

### ✅ **Smart Cooldown System**
- Trade closes → 4-hour cooldown starts
- Prevents over-trading same pair
- Pair still monitored but no new signals

### ✅ **Live Monitoring**
- Checks prices every 15 minutes
- Auto-detects stop/target hits
- Calculates P&L automatically

---

## 📈 **Understanding Current Status**

From the verification script, you'll see:

```
Active Trades: 19      ← Trades currently running
Cooldown Trades: 1     ← Pairs in 4-hour cooldown
Total Completed: 1     ← Trades that hit stop/target
```

**This means:**
- 19 pairs are blocked (have active trades)
- 1 pair is blocked (in cooldown)
- 9 pairs available for new signals (29 total - 19 active - 1 cooldown = 9 free)

---

## 🎯 **What to Expect Going Forward**

### **You'll Receive Fewer Signals**
- **Why?** Each pair can only have 1 active trade
- **Good Thing:** No more contradictory positions
- **Result:** Cleaner, more manageable trading

### **4-Hour Gaps Between Signals (Same Pair)**
- **Why?** Cooldown period after trade closes
- **Good Thing:** Prevents emotional over-trading
- **Result:** More disciplined approach

### **No More "Batch Spam"**
- **Why?** Trade tracking prevents duplicate signals
- **Good Thing:** Each signal is meaningful
- **Result:** No more 10+ signals at once for same pairs

---

## 🔧 **Customize Settings**

### **Change Cooldown Duration:**
Edit `trade_tracker.py`, line 20:
```python
self.cooldown_hours = 4  # Change to 2, 6, 8, etc.
```

### **Change Monitoring Frequency:**
Edit `yahoo_forex_bot.py`, line 611:
```python
time.sleep(15 * 60)  # Change to 10*60, 20*60, 30*60, etc.
```

---

## 📞 **If Something Goes Wrong**

### **Bot Not Generating Signals?**
1. Run `python3 verify_trade_tracking.py`
2. Check how many active trades exist
3. If 29 active trades = all pairs blocked (wait for some to close)

### **Trade Not Closing?**
1. Check if price actually hit stop/target
2. Wait for next 15-minute monitoring cycle
3. Verify Yahoo Finance data is available

### **Files Missing?**
1. Run `python3 trade_tracker.py` (creates files)
2. Restart bot: `pkill -f yahoo_forex_bot && python3 yahoo_forex_bot.py &`

---

## ✅ **Quick Health Check**

Run this to verify everything is working:

```bash
echo "🤖 Bot Status:" && ps aux | grep yahoo_forex_bot | grep -v grep || echo "   ❌ Bot not running"
echo ""
echo "📊 Dashboard Status:" && ps aux | grep dashboard_server_mac | grep -v grep || echo "   ❌ Dashboard not running"
echo ""
echo "📁 Files:" && ls -lh *.json | grep -E "(active_trades|cooldown_trades|trade_history)" || echo "   ❌ Trade files missing"
echo ""
python3 verify_trade_tracking.py
```

---

**Phase A is complete! The bot now has intelligent trade tracking and won't give contradictory signals.** 🎉


