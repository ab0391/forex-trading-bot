#!/usr/bin/env python3
"""
Automatic Trade Tracker
Uses Yahoo Finance data to automatically determine if trades hit stop or target
"""

import yfinance as yf
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoTradeTracker:
    """Automatically track trades using real market data"""
    
    def __init__(self):
        self.trades_file = Path("trades_history.json")
        self.risk_per_trade = 10.00
    
    def get_yahoo_symbol(self, symbol):
        """Convert our symbol format to Yahoo Finance format"""
        if '/' in symbol:
            return symbol.replace('/', '') + '=X'
        elif symbol == 'GOLD':
            return 'GC=F'
        elif symbol == 'SILVER':
            return 'SI=F'
        elif symbol == 'OIL':
            return 'CL=F'
        elif symbol == 'BITCOIN':
            return 'BTC-USD'
        elif symbol == 'ETHEREUM':
            return 'ETH-USD'
        else:
            return symbol
    
    def check_trade_outcome(self, trade):
        """Check if trade hit stop or target using historical data"""
        try:
            symbol = trade['symbol']
            entry = trade['entry']
            stop = trade['stop']
            target = trade['target']
            direction = trade['direction']
            entry_time = trade['timestamp']
            
            # Get Yahoo Finance symbol
            yf_symbol = self.get_yahoo_symbol(symbol)
            
            logger.info(f"Checking {symbol} ({yf_symbol})...")
            
            # Get historical data since entry
            ticker = yf.Ticker(yf_symbol)
            
            # Get data from entry time until now
            entry_date = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
            hist = ticker.history(start=entry_date, interval='1h')
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return None, None
            
            logger.info(f"  Checking {len(hist)} candles since entry...")
            logger.info(f"  Entry: {entry:.5f}, Stop: {stop:.5f}, Target: {target:.5f}")
            logger.info(f"  Direction: {direction}")
            
            # Check if stop or target was hit
            if direction == 'SHORT':
                # For shorts: loss if price goes above stop, win if below target
                stop_hit = (hist['High'] >= stop).any()
                target_hit = (hist['Low'] <= target).any()
                
                if stop_hit and target_hit:
                    # Both hit - which came first?
                    stop_idx = hist[hist['High'] >= stop].index[0]
                    target_idx = hist[hist['Low'] <= target].index[0]
                    
                    if stop_idx < target_idx:
                        logger.info(f"  ❌ Stop hit first at {stop_idx}")
                        return 'loss', hist.loc[stop_idx, 'High']
                    else:
                        logger.info(f"  ✅ Target hit first at {target_idx}")
                        return 'win', hist.loc[target_idx, 'Low']
                
                elif stop_hit:
                    logger.info(f"  ❌ Stop hit")
                    return 'loss', hist[hist['High'] >= stop]['High'].iloc[0]
                
                elif target_hit:
                    logger.info(f"  ✅ Target hit")
                    return 'win', hist[hist['Low'] <= target]['Low'].iloc[0]
                
            else:  # LONG
                # For longs: loss if price goes below stop, win if above target
                stop_hit = (hist['Low'] <= stop).any()
                target_hit = (hist['High'] >= target).any()
                
                if stop_hit and target_hit:
                    # Both hit - which came first?
                    stop_idx = hist[hist['Low'] <= stop].index[0]
                    target_idx = hist[hist['High'] >= target].index[0]
                    
                    if stop_idx < target_idx:
                        logger.info(f"  ❌ Stop hit first at {stop_idx}")
                        return 'loss', hist.loc[stop_idx, 'Low']
                    else:
                        logger.info(f"  ✅ Target hit first at {target_idx}")
                        return 'win', hist.loc[target_idx, 'High']
                
                elif stop_hit:
                    logger.info(f"  ❌ Stop hit")
                    return 'loss', hist[hist['Low'] <= stop]['Low'].iloc[0]
                
                elif target_hit:
                    logger.info(f"  ✅ Target hit")
                    return 'win', hist[hist['High'] >= target]['High'].iloc[0]
            
            logger.info(f"  🔵 Still active (neither stop nor target hit)")
            return 'active', None
            
        except Exception as e:
            logger.error(f"Error checking {symbol}: {e}")
            return None, None
    
    def update_all_trades(self):
        """Auto-update all trades based on market data"""
        if not self.trades_file.exists():
            logger.error("No trades file found")
            return
        
        with open(self.trades_file, 'r') as f:
            trades = json.load(f)
        
        updated_count = 0
        completed_count = 0
        
        for trade in trades:
            if trade['status'] == 'active':
                result, close_price = self.check_trade_outcome(trade)
                
                if result in ['win', 'loss']:
                    trade['status'] = result
                    trade['close_time'] = datetime.now().isoformat()
                    trade['close_price'] = close_price
                    
                    if result == 'win':
                        trade['pnl'] = trade['potential_profit']
                        logger.info(f"✅ {trade['symbol']} WON: +${trade['pnl']:.2f}")
                    else:
                        trade['pnl'] = -trade['risk_amount']
                        logger.info(f"❌ {trade['symbol']} LOST: ${trade['pnl']:.2f}")
                    
                    updated_count += 1
                    completed_count += 1
        
        # Save updated trades
        with open(self.trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
        
        # Calculate final stats
        completed = [t for t in trades if t['status'] in ['win', 'loss', 'breakeven']]
        wins = [t for t in trades if t['status'] == 'win']
        losses = [t for t in trades if t['status'] == 'loss']
        total_pnl = sum(t['pnl'] for t in completed)
        
        logger.info(f"\n📊 Auto-Tracking Results:")
        logger.info(f"   Updated: {updated_count} trades")
        logger.info(f"   Completed: {len(completed)} total")
        logger.info(f"   Wins: {len(wins)}")
        logger.info(f"   Losses: {len(losses)}")
        logger.info(f"   Net P&L: ${total_pnl:.2f}")
        
        return trades

if __name__ == "__main__":
    tracker = AutoTradeTracker()
    trades = tracker.update_all_trades()
    
    print("\n" + "="*60)
    print("📊 FINAL TRADE SUMMARY")
    print("="*60)
    
    completed = [t for t in trades if t['status'] in ['win', 'loss']]
    active = [t for t in trades if t['status'] == 'active']
    
    print(f"\n✅ Completed Trades: {len(completed)}")
    for trade in completed:
        emoji = "✅" if trade['status'] == 'win' else "❌"
        print(f"   {emoji} {trade['symbol']} - {trade['status'].upper()} - ${trade['pnl']:.2f}")
    
    print(f"\n🔵 Active Trades: {len(active)}")
    for trade in active[:5]:  # Show first 5
        print(f"   🔵 {trade['symbol']} - {trade['direction']} - Risk: ${trade['risk_amount']:.2f}")
    
    if len(active) > 5:
        print(f"   ... and {len(active) - 5} more active trades")
    
    total_pnl = sum(t['pnl'] for t in completed)
    print(f"\n💰 Net P&L: ${total_pnl:.2f}")
    print("="*60)
