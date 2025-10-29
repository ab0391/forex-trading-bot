#!/usr/bin/env python3
"""
Advanced Trade Tracking System
Prevents contradictory signals and tracks active trades
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TradeTracker:
    """Track active trades and prevent contradictory signals"""
    
    def __init__(self):
        self.active_trades_file = Path("active_trades.json")
        self.trade_history_file = Path("trade_history.json")
        self.cooldown_file = Path("cooldown_trades.json")
        self.cooldown_hours = 4  # 4-hour cooldown after trade closure
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize tracking files if they don't exist"""
        if not self.active_trades_file.exists():
            with open(self.active_trades_file, 'w') as f:
                json.dump([], f)
        
        if not self.trade_history_file.exists():
            with open(self.trade_history_file, 'w') as f:
                json.dump([], f)
        
        if not self.cooldown_file.exists():
            with open(self.cooldown_file, 'w') as f:
                json.dump([], f)
    
    def load_active_trades(self):
        """Load currently active trades"""
        try:
            with open(self.active_trades_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading active trades: {e}")
            return []
    
    def load_cooldown_trades(self):
        """Load trades in cooldown period"""
        try:
            with open(self.cooldown_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cooldown trades: {e}")
            return []
    
    def save_active_trades(self, trades):
        """Save active trades to file"""
        try:
            with open(self.active_trades_file, 'w') as f:
                json.dump(trades, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving active trades: {e}")
    
    def save_cooldown_trades(self, trades):
        """Save cooldown trades to file"""
        try:
            with open(self.cooldown_file, 'w') as f:
                json.dump(trades, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cooldown trades: {e}")
    
    def add_active_trade(self, signal):
        """Add a new active trade"""
        active_trades = self.load_active_trades()
        
        # Create trade record
        trade = {
            'trade_id': signal['signal_id'],
            'symbol': signal['symbol'],
            'direction': 'LONG' if signal['zone_type'] == 'demand' else 'SHORT',
            'zone_type': signal['zone_type'],
            'entry': signal['entry'],
            'stop': signal['stop'],
            'target': signal['target'],
            'risk_reward': signal['risk_reward'],
            'timestamp': signal['timestamp'],
            'status': 'active',
            'last_checked': datetime.now().isoformat()
        }
        
        active_trades.append(trade)
        self.save_active_trades(active_trades)
        
        logger.info(f"✅ Added active trade: {trade['symbol']} {trade['direction']}")
        return trade
    
    def can_generate_signal(self, symbol):
        """Check if we can generate a new signal for this symbol"""
        # Check if symbol has active trade
        active_trades = self.load_active_trades()
        for trade in active_trades:
            if trade['symbol'] == symbol and trade['status'] == 'active':
                logger.info(f"⏸️ {symbol}: Active trade exists, skipping signal")
                return False
        
        # Check if symbol is in cooldown
        cooldown_trades = self.load_cooldown_trades()
        current_time = datetime.now()
        
        for trade in cooldown_trades:
            if trade['symbol'] == symbol:
                # Check if cooldown period has expired
                trade_time = datetime.fromisoformat(trade['closed_at'])
                if current_time - trade_time < timedelta(hours=self.cooldown_hours):
                    remaining_time = timedelta(hours=self.cooldown_hours) - (current_time - trade_time)
                    logger.info(f"⏰ {symbol}: In cooldown for {remaining_time}")
                    return False
                else:
                    # Remove expired cooldown
                    cooldown_trades.remove(trade)
                    self.save_cooldown_trades(cooldown_trades)
        
        return True
    
    def check_trade_outcomes(self, current_prices):
        """Check if any active trades have hit stop or target"""
        active_trades = self.load_active_trades()
        updated_trades = []
        closed_trades = []
        
        for trade in active_trades:
            symbol = trade['symbol']
            current_price = current_prices.get(symbol)
            
            if current_price is None:
                # Keep trade active if we can't get current price
                updated_trades.append(trade)
                continue
            
            # Check if trade hit stop or target
            hit_stop = False
            hit_target = False
            outcome = None
            
            if trade['direction'] == 'LONG':
                if current_price <= trade['stop']:
                    hit_stop = True
                    outcome = 'loss'
                elif current_price >= trade['target']:
                    hit_target = True
                    outcome = 'win'
            else:  # SHORT
                if current_price >= trade['stop']:
                    hit_stop = True
                    outcome = 'loss'
                elif current_price <= trade['target']:
                    hit_target = True
                    outcome = 'win'
            
            if hit_stop or hit_target:
                # Close the trade
                trade['status'] = outcome
                trade['closed_at'] = datetime.now().isoformat()
                trade['close_price'] = current_price
                trade['last_checked'] = datetime.now().isoformat()
                
                # Calculate P&L
                if trade['direction'] == 'LONG':
                    pnl = (current_price - trade['entry']) * 10000  # Assuming 1 lot = $10,000
                else:
                    pnl = (trade['entry'] - current_price) * 10000
                
                trade['pnl'] = pnl
                closed_trades.append(trade)
                
                # Add to cooldown
                self._add_to_cooldown(trade)
                
                logger.info(f"🎯 {symbol} {trade['direction']}: {outcome.upper()} at {current_price} (P&L: ${pnl:.2f})")
            else:
                # Keep trade active
                trade['last_checked'] = datetime.now().isoformat()
                updated_trades.append(trade)
        
        # Save updated active trades
        self.save_active_trades(updated_trades)
        
        # Save closed trades to history
        if closed_trades:
            self._save_to_history(closed_trades)
        
        return len(closed_trades)
    
    def _add_to_cooldown(self, trade):
        """Add trade to cooldown period"""
        cooldown_trades = self.load_cooldown_trades()
        
        cooldown_entry = {
            'symbol': trade['symbol'],
            'direction': trade['direction'],
            'outcome': trade['status'],
            'closed_at': trade['closed_at'],
            'cooldown_until': (datetime.now() + timedelta(hours=self.cooldown_hours)).isoformat()
        }
        
        cooldown_trades.append(cooldown_entry)
        self.save_cooldown_trades(cooldown_trades)
    
    def _save_to_history(self, closed_trades):
        """Save closed trades to history"""
        try:
            with open(self.trade_history_file, 'r') as f:
                data = json.load(f)
                # Handle both old dict format and new list format
                if isinstance(data, dict):
                    history = data.get('completed_trades', [])
                else:
                    history = data
        except:
            history = []
        
        history.extend(closed_trades)
        
        # Keep only last 1000 trades
        if len(history) > 1000:
            history = history[-1000:]
        
        with open(self.trade_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_trade_stats(self):
        """Get comprehensive trade statistics"""
        try:
            with open(self.trade_history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
        
        active_trades = self.load_active_trades()
        cooldown_trades = self.load_cooldown_trades()
        
        # Calculate statistics
        total_trades = len(history)
        wins = len([t for t in history if t.get('status') == 'win'])
        losses = len([t for t in history if t.get('status') == 'loss'])
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t.get('pnl', 0) for t in history)
        
        stats = {
            'active_trades': len(active_trades),
            'cooldown_trades': len(cooldown_trades),
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'active_symbols': [t['symbol'] for t in active_trades],
            'cooldown_symbols': [t['symbol'] for t in cooldown_trades]
        }
        
        return stats
    
    def cleanup_expired_cooldowns(self):
        """Remove expired cooldown entries"""
        cooldown_trades = self.load_cooldown_trades()
        current_time = datetime.now()
        
        active_cooldowns = []
        for trade in cooldown_trades:
            cooldown_until = datetime.fromisoformat(trade['cooldown_until'])
            if current_time < cooldown_until:
                active_cooldowns.append(trade)
        
        if len(active_cooldowns) != len(cooldown_trades):
            self.save_cooldown_trades(active_cooldowns)
            logger.info(f"🧹 Cleaned up {len(cooldown_trades) - len(active_cooldowns)} expired cooldowns")

# Test the trade tracker
if __name__ == "__main__":
    tracker = TradeTracker()
    
    # Test with sample signal
    sample_signal = {
        'signal_id': 'TEST_supply_1234567890',
        'symbol': 'EUR/USD',
        'zone_type': 'supply',
        'entry': 1.1000,
        'stop': 1.1050,
        'target': 1.0900,
        'risk_reward': 2.0,
        'timestamp': datetime.now().isoformat()
    }
    
    print("🧪 Testing Trade Tracker...")
    print(f"Can generate signal for EUR/USD: {tracker.can_generate_signal('EUR/USD')}")
    
    # Add test trade
    tracker.add_active_trade(sample_signal)
    print(f"Can generate signal for EUR/USD after adding trade: {tracker.can_generate_signal('EUR/USD')}")
    
    # Get stats
    stats = tracker.get_trade_stats()
    print(f"Trade Stats: {stats}")