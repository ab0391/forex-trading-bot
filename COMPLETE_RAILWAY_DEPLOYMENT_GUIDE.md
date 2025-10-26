# 🚀 Complete Railway Deployment Guide - 24/7 Trading Bots

## 🎯 Overview
Both trading bots are now ready for 24/7 deployment on Railway:

1. **Forex Trading Bot**: https://github.com/ab0391/forex-trading-bot
2. **Stock Trading Bot (ORB Strategy)**: https://github.com/ab0391/stock-trading-bot

## 📱 Telegram Bot Credentials

### **Forex Bot:**
- **Bot Token**: `8294375530:AAGpvxGD54ejEt9LXlZejQV8ZxtMxnXb0R8`
- **Bot Username**: `@fx_pairs_bot`
- **Bot URL**: `t.me/fx_pairs_bot`

### **Stock Bot:**
- **Bot Token**: `8212205627:AAEpn-8ReZkBtoI4iHJbJxcHn8llSj2JtY4`
- **Bot Username**: `@breakout_trading_bot`
- **Bot URL**: `t.me/Breakout_trading_bot`

## 🚀 Railway Deployment Steps

### **Step 1: Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with your GitHub account (`ab0391`)
4. Connect your GitHub repositories

### **Step 2: Deploy Forex Trading Bot**
1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `ab0391/forex-trading-bot`
4. Railway will auto-detect Python app
5. **Add Environment Variables:**
   - Click on your project → Variables tab
   - Add: `TELEGRAM_BOT_TOKEN` = `8294375530:AAGpvxGD54ejEt9LXlZejQV8ZxtMxnXb0R8`
   - Add: `TELEGRAM_CHAT_ID` = `your_chat_id_here` (replace with your actual chat ID)
6. Click "Deploy" - it will start automatically!

### **Step 3: Deploy Stock Trading Bot**
1. Create another project in Railway
2. Select "Deploy from GitHub repo"
3. Choose `ab0391/stock-trading-bot`
4. **Add Environment Variables:**
   - `TELEGRAM_TOKEN` = `8212205627:AAEpn-8ReZkBtoI4iHJbJxcHn8llSj2JtY4`
   - `TELEGRAM_CHAT_ID` = `your_chat_id_here` (replace with your actual chat ID)
   - `ACCOUNT_SIZE` = `50000` (or your account size)
   - `RISK_PER_TRADE` = `0.01` (1% risk per trade)
5. Deploy!

## 📊 What Each Bot Does

### **Forex Trading Bot Features:**
- ✅ **29 Forex Pairs** with Yahoo Finance API
- ✅ **Smart Market Hours** detection
- ✅ **Telegram Signal Processing** via `@fx_pairs_bot`
- ✅ **Trade Tracking** and history
- ✅ **Dashboard Server** for monitoring
- ✅ **Rate Limit Free** (Yahoo Finance)
- ✅ **24/7 Operation** ready

### **Stock Trading Bot Features (ORB Strategy):**
- ✅ **Opening Range Breakout** strategy implemented
- ✅ **8 Major Stocks**: AAPL, TSLA, MSFT, GOOGL, AMZN, META, NVDA, NFLX
- ✅ **Risk Management**: 2:1 minimum risk-reward ratio
- ✅ **Position Sizing**: 1-2% risk per trade
- ✅ **Multiple Take Profits**: TP1, TP2, TP3 with scaling
- ✅ **Trailing Stops**: After TP1 hit
- ✅ **Time-based Exits**: Close by 3:45 PM EST
- ✅ **Volume Confirmation**: 1.5x average volume required
- ✅ **Telegram Integration** via `@breakout_trading_bot`

## 🔧 Environment Variables Required

### **Forex Bot:**
```
TELEGRAM_BOT_TOKEN=8294375530:AAGpvxGD54ejEt9LXlZejQV8ZxtMxnXb0R8
TELEGRAM_CHAT_ID=your_chat_id_here
```

### **Stock Bot:**
```
TELEGRAM_TOKEN=8212205627:AAEpn-8ReZkBtoI4iHJbJxcHn8llSj2JtY4
TELEGRAM_CHAT_ID=your_chat_id_here
ACCOUNT_SIZE=50000
RISK_PER_TRADE=0.01
```

## 📈 ORB Strategy Details

### **Opening Range Period:**
- **Time**: 9:30 AM - 10:00 AM EST (first 30 minutes)
- **Calculation**: High and Low of opening range
- **Breakout Confirmation**: Volume 1.5x average + candle close

### **Entry Conditions:**
- **Long**: Price breaks above Opening Range High (ORH)
- **Short**: Price breaks below Opening Range Low (ORL)
- **Volume**: Must be 1.5x the 20-period average

### **Risk Management:**
- **Stop Loss**: ORL - $0.10 (Long) or ORH + $0.10 (Short)
- **Target 1**: 2:1 Risk-Reward ratio
- **Target 2**: 3:1 Risk-Reward ratio
- **Target 3**: 2x Opening Range size
- **Position Sizing**: Based on 1-2% account risk

### **Trade Management:**
- **Scaling**: 50% at TP1, 25% at TP2, 25% trailed
- **Trailing Stop**: Move to breakeven after TP1
- **Time Exit**: Close all positions by 3:45 PM EST
- **Daily Limits**: Max 3 trades per day, 3% daily loss limit

## 🎯 Next Steps After Deployment

1. **Get Your Chat ID:**
   - Message @userinfobot on Telegram
   - Copy your chat ID number
   - Update the environment variables in Railway

2. **Test the Bots:**
   - Check Railway logs for any errors
   - Send test messages to your Telegram bots
   - Verify market data is being received

3. **Monitor Performance:**
   - Check Railway dashboard for resource usage
   - Monitor Telegram for trading signals
   - Review trade history and performance

## 💡 Railway Benefits

- ✅ **24/7 Operation**: Bots run continuously
- ✅ **Automatic Restarts**: If bot crashes, Railway restarts it
- ✅ **No Local Dependencies**: Runs in the cloud
- ✅ **Easy Monitoring**: Railway dashboard shows logs and status
- ✅ **Cost Effective**: Pay only for what you use
- ✅ **Scalable**: Can handle multiple bots simultaneously

## 🔍 Monitoring Your Bots

### **Railway Dashboard:**
- View real-time logs
- Monitor resource usage (CPU, Memory)
- Check deployment status
- Restart services if needed

### **Telegram Notifications:**
- **Forex Bot**: Signals for 29 forex pairs
- **Stock Bot**: ORB breakouts for 8 major stocks
- **Trade Updates**: Entry, exit, and P&L notifications

## 📞 Support

If you need help with:
- Railway deployment issues
- Telegram configuration
- Strategy modifications
- Performance optimization

Just let me know! The bots are fully implemented and ready for 24/7 operation.

---

## 🎉 **Ready to Deploy!**

Both bots are now:
- ✅ **Fully implemented** with your strategies
- ✅ **Telegram integrated** with correct credentials
- ✅ **GitHub uploaded** and ready for deployment
- ✅ **Railway configured** for 24/7 operation

**Your automated trading empire is ready to go live! 🚀**
