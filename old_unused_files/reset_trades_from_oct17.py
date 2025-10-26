#!/usr/bin/env python3
"""
Reset trades to only include the 4 completed trades from Oct 17th forward
Based on user's actual trading history
"""

import json
from pathlib import Path
from datetime import datetime

def reset_trades():
    """Reset to only the 4 completed trades and going forward"""
    
    # The 4 completed trades from user's history
    completed_trades = [
        {
            "trade_id": "AUDCAD_2025-10-13_00:01:14",
            "symbol": "AUD/CAD",
            "direction": "SHORT",
            "entry": 0.90868,
            "stop": 0.91311,  # Approximate stop based on loss
            "target": 0.90418,  # Approximate target (2:1 R:R)
            "timestamp": "2025-10-13T00:01:14Z",
            "status": "loss",
            "close_time": "2025-10-13T00:01:14Z",
            "close_price": 0.91311,
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": -10.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        },
        {
            "trade_id": "GBPCHF_2025-10-17_10:02:54",
            "symbol": "GBP/CHF", 
            "direction": "SHORT",
            "entry": 1.07172,
            "stop": 1.07672,  # Approximate stop
            "target": 1.06172,  # Actual exit price
            "timestamp": "2025-10-17T10:02:54Z",
            "status": "win",
            "close_time": "2025-10-17T10:02:54Z",
            "close_price": 1.06100,
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": 20.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        },
        {
            "trade_id": "GBPCHF_2025-10-17_10:09:46",
            "symbol": "GBP/CHF",
            "direction": "SHORT", 
            "entry": 1.06932,
            "stop": 1.07432,  # Approximate stop
            "target": 1.05932,  # Actual exit price
            "timestamp": "2025-10-17T10:09:46Z",
            "status": "win",
            "close_time": "2025-10-17T10:09:46Z",
            "close_price": 1.05873,
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": 20.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        },
        {
            "trade_id": "EURGBP_2025-10-17_11:16:16",
            "symbol": "EUR/GBP",
            "direction": "SHORT",
            "entry": 0.86814,
            "stop": 0.87314,  # Approximate stop
            "target": 0.86314,  # Approximate target
            "timestamp": "2025-10-17T11:16:16Z",
            "status": "loss",
            "close_time": "2025-10-17T11:16:16Z",
            "close_price": 0.87250,
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": -10.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        }
    ]
    
    # The 4 active trades mentioned by user
    active_trades = [
        {
            "trade_id": "AUDCAD_active_2025-10-18",
            "symbol": "AUD/CAD",
            "direction": "SHORT",
            "entry": 0.91051,  # From recent signal
            "stop": 0.91506,
            "target": 0.90140,
            "timestamp": "2025-10-18T09:00:00Z",
            "status": "active",
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": 0.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        },
        {
            "trade_id": "EURCHF_active_2025-10-18",
            "symbol": "EUR/CHF",
            "direction": "SHORT",
            "entry": 0.93042,  # From recent signal
            "stop": 0.93507,
            "target": 0.92112,
            "timestamp": "2025-10-18T09:00:00Z",
            "status": "active",
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": 0.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        },
        {
            "trade_id": "EURGBP_active_2025-10-18",
            "symbol": "EUR/GBP",
            "direction": "SHORT",
            "entry": 0.86816,  # From recent signal
            "stop": 0.87266,
            "target": 0.85916,
            "timestamp": "2025-10-18T09:00:00Z",
            "status": "active",
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": 0.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        },
        {
            "trade_id": "GBPUSD_active_2025-10-18",
            "symbol": "GBP/USD",
            "direction": "SHORT",
            "entry": 1.34205,  # From recent signal
            "stop": 1.34876,
            "target": 1.32863,
            "timestamp": "2025-10-18T09:00:00Z",
            "status": "active",
            "risk_amount": 10.00,
            "potential_profit": 20.00,
            "pnl": 0.00,
            "risk_reward": 2.0,
            "zone_type": "supply"
        }
    ]
    
    # Combine all trades
    all_trades = completed_trades + active_trades
    
    # Save to trades_history.json
    trades_file = Path("trades_history.json")
    with open(trades_file, 'w') as f:
        json.dump(all_trades, f, indent=2)
    
    print("✅ Reset trades successfully!")
    print(f"📊 Total trades: {len(all_trades)}")
    print(f"✅ Completed: {len(completed_trades)} (2 wins, 2 losses)")
    print(f"🔵 Active: {len(active_trades)}")
    print(f"💰 Net P&L: +$20.00 (2×$20 - 2×$10)")
    
    return all_trades

if __name__ == "__main__":
    reset_trades()
