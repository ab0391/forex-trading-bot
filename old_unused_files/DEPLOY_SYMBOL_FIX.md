# 🚀 DEPLOY SYMBOL RATE LIMITING FIX

## 🎯 IMMEDIATE ACTION REQUIRED

The TwelveData credit spikes are caused by scanning **5 symbols × 4 API calls = 20 calls per cycle**. This creates 6+ credit bursts exceeding the 8/minute limit.

## 📦 FILES READY FOR DEPLOYMENT

1. **`complete_enhanced_trading_bot_optimized.py`** - Updated with 2-symbol limit
2. **`enhanced_symbol_rotation_bot.py`** - Future enhancement with rotation
3. **`DEPLOY_SYMBOL_FIX.md`** - This deployment guide

## 🚨 PHASE 1: IMMEDIATE FIX (DEPLOY NOW)

### **Option A: Claude Code Deployment**
```
The trading bot is using too many API calls because it scans 5 symbols × 4 calls each = 20 calls per cycle, causing TwelveData credit spikes.

URGENT FIX: In complete_enhanced_trading_bot_optimized.py, line 766, change:

FROM:
self.symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]

TO:
# 🛡️ SYMBOL RATE LIMITING: Reduced from 5 to 2 symbols to stay under API limit
# 2 symbols × 4 calls each = 8 calls = exactly at 8/minute limit  
self.symbols = ["EUR/USD", "GBP/USD"]  # Most liquid pairs for reliable signals

This will immediately reduce API usage from 20 calls to 8 calls per cycle, eliminating the credit spikes shown in the TwelveData dashboard.

Deploy this change to the Oracle server immediately and restart the trading service.
```

### **Option B: Manual Server Deployment**
```bash
# 1. Upload fixed file to server
scp complete_enhanced_trading_bot_optimized.py username@server:/home/ubuntu/fxbot/

# 2. SSH to server and deploy
ssh username@server
cd /home/ubuntu/fxbot

# 3. Backup current version
cp complete_enhanced_trading_bot_fixed.py complete_enhanced_trading_bot_backup_$(date +%Y%m%d_%H%M%S).py

# 4. Deploy 2-symbol fix
cp complete_enhanced_trading_bot_optimized.py complete_enhanced_trading_bot_fixed.py

# 5. Restart service
sudo systemctl restart fxbot-run.service

# 6. Monitor immediately
journalctl -u fxbot-run.service -f
```

## 📊 EXPECTED RESULTS (WITHIN 1 HOUR)

### **TwelveData Dashboard Changes:**
- **Minutely maximum**: 8/8 → 7/8 (at or under limit)
- **Graph pattern**: Consistent ~2 credit bars instead of 6+ spikes
- **No red areas**: All usage under the red limit line
- **Smooth pattern**: No more alternating big/small spikes

### **Bot Behavior:**
- **Scans**: EUR/USD and GBP/USD only (most liquid pairs)
- **API calls**: Exactly 8 per cycle (2 symbols × 4 calls)
- **Timing**: ~2-3 minutes per complete scan
- **Signals**: Focused on highest-quality pairs

## 🔄 PHASE 2: ENHANCED ROTATION (FUTURE)

Once Phase 1 is confirmed working, implement the rotation system:

```python
# Enhanced version that covers all 5 symbols across multiple cycles
# Cycle 1: EUR/USD, GBP/USD (8 calls)
# Cycle 2: USD/JPY, AUD/USD (8 calls)  
# Cycle 3: USD/CHF, EUR/USD (8 calls)
# Result: All symbols covered, never exceeding limit
```

## ⏱️ MONITORING CHECKLIST

**Immediate (0-30 minutes):**
- [ ] Bot successfully started with 2 symbols
- [ ] No error messages in logs
- [ ] API calls showing proper rate limiting

**Short term (1-2 hours):**
- [ ] TwelveData minutely maximum ≤8/8
- [ ] Graph shows consistent small bars
- [ ] No credit spikes above limit line

**Daily (24 hours):**
- [ ] Total API usage significantly reduced
- [ ] Bot still generating quality signals
- [ ] No rate limit violations in TwelveData

## 🚨 CRITICAL SUCCESS METRICS

**Before fix**: Minutely maximum 9/8 (RED - over limit)
**After fix**: Minutely maximum ≤7/8 (GREEN - under limit)

**Deploy this fix immediately to resolve the credit spike issue!**
