#!/usr/bin/env python3
"""
Send a sample trading signal to Telegram
Shows what real alerts will look like
"""

from complete_enhanced_trading_bot_optimized import TelegramNotifier

notifier = TelegramNotifier()

# Send a sample trading signal
print("📤 Sending sample trading signal to Telegram...")

success = notifier.send_trading_alert(
    symbol='EUR/USD',
    zone_type='demand',
    entry=1.08567,
    stop=1.08234,
    target=1.09230,
    rr=2.0,
    bias_info='H4 bullish bias (87% confidence) aligned with daily support',
    current_price=1.08634
)

if success:
    print("✅ Sample trading signal sent!")
    print("📱 Check your Telegram to see what real alerts look like")
else:
    print("❌ Failed to send signal")

