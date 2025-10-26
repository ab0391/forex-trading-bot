#!/usr/bin/env python3
"""
Fix trades - mark the 4th completed trade (2nd GBP/CHF)
"""

import json
from pathlib import Path

trades_file = Path("trades_history.json")

with open(trades_file, 'r') as f:
    trades = json.load(f)

# Find the second GBP/CHF (Oct 11) and mark it as completed
gbpchf_found = 0
for trade in trades:
    if trade['symbol'] == 'GBP/CHF' and trade['timestamp'].startswith('2025-10-11'):
        if trade['status'] == 'active':
            trade['status'] = 'win'
            trade['pnl'] = trade['potential_profit']
            trade['close_time'] = '2025-10-17T12:00:00'
            print(f"✅ Marked {trade['symbol']} (Oct 11) as COMPLETED WIN: +${trade['pnl']:.2f}")
            gbpchf_found += 1
            break

with open(trades_file, 'w') as f:
    json.dump(trades, f, indent=2)

# Print summary
completed = [t for t in trades if t['status'] in ['win', 'loss', 'breakeven']]
active = [t for t in trades if t['status'] == 'active']
wins = [t for t in trades if t['status'] == 'win']
total_pnl = sum(t['pnl'] for t in completed)

print(f"\n📊 Final Trade Status:")
print(f"   Completed: {len(completed)} ({len(wins)} wins)")
print(f"   Active: {len(active)}")
print(f"   Net P&L: ${total_pnl:.2f}")
print(f"   Win Rate: {len(wins)/len(completed)*100:.1f}%")

print(f"\n✅ Completed Trades:")
for trade in completed:
    print(f"   {trade['symbol']} ({trade['timestamp'][:10]}) - ${trade['pnl']:.2f}")
