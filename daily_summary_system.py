#!/usr/bin/env python3
"""
Daily Summary System for Trading Bots
Provides end-of-day summaries and market close notifications
"""

import json
import logging
import requests
from datetime import datetime, time, timedelta
import pytz
from typing import List, Dict, Any

# Try to import market calendars, fallback to simple weekend check
try:
    import pandas_market_calendars as mcal
    MARKET_CALENDARS_AVAILABLE = True
except ImportError:
    MARKET_CALENDARS_AVAILABLE = False
    logging.warning("⚠️ pandas-market-calendars not available, using weekend-only checks")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailySummarySystem:
    def __init__(self, telegram_token: str, chat_id: str):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.dubai_tz = pytz.timezone('Asia/Dubai')
        self.london_tz = pytz.timezone('Europe/London')
        self.ny_tz = pytz.timezone('America/New_York')
        
        # Initialize market calendars for holiday detection
        if MARKET_CALENDARS_AVAILABLE:
            try:
                self.nyse = mcal.get_calendar('NYSE')
                self.lse = mcal.get_calendar('LSE')
                logger.info("✅ Market calendars loaded (NYSE, LSE)")
            except Exception as e:
                logger.warning(f"⚠️ Could not load market calendars: {e}")
                self.nyse = None
                self.lse = None
        else:
            self.nyse = None
            self.lse = None
            logger.info("⚠️ Using weekend-only checks (market calendars not available)")
        
    def send_telegram_message(self, message: str):
        """Send message via Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Telegram message sent successfully")
                return True
            else:
                logger.error(f"❌ Telegram error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
    
    def get_forex_daily_summary(self) -> str:
        """Generate forex bot daily summary"""
        try:
            # Load active trades (gracefully handle missing file)
            try:
                with open('active_trades.json', 'r') as f:
                    active_trades = json.load(f)
            except FileNotFoundError:
                logger.warning("⚠️ active_trades.json not found - treating as no active trades")
                active_trades = []
            
            # Load completed trades from today (gracefully handle missing file)
            try:
                with open('trade_history.json', 'r') as f:
                    history_data = json.load(f)
            except FileNotFoundError:
                logger.warning("⚠️ trade_history.json not found - treating as no completed trades")
                history_data = []
            
            # Handle both dict and list formats
            if isinstance(history_data, dict):
                completed_trades = history_data.get('completed_trades', [])
            else:
                completed_trades = history_data
            
            # Filter today's completed trades
            today = datetime.now(self.dubai_tz).date()
            today_trades = []
            for trade in completed_trades:
                try:
                    trade_date = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00')).date()
                    if trade_date == today:
                        today_trades.append(trade)
                except:
                    continue
            
            # Generate summary
            summary = f"""
📊 <b>FOREX BOT DAILY SUMMARY</b>
🕐 Time: {datetime.now(self.dubai_tz).strftime('%H:%M:%S')} Dubai
📅 Date: {today.strftime('%Y-%m-%d')}

📈 <b>ACTIVE TRADES ({len(active_trades)})</b>
"""
            
            if active_trades:
                for trade in active_trades:
                    direction_emoji = "🟢" if trade['direction'] == 'LONG' else "🔴"
                    summary += f"{direction_emoji} <b>{trade['symbol']}</b> {trade['direction']}\n"
                    summary += f"   Entry: {trade['entry']} | Stop: {trade['stop']} | Target: {trade['target']}\n"
                    summary += f"   R:R: {trade['risk_reward']:.1f}:1 | Status: {trade['status']}\n\n"
            else:
                summary += "No active trades\n\n"
            
            summary += f"📊 <b>TODAY'S COMPLETED TRADES ({len(today_trades)})</b>\n"
            
            if today_trades:
                wins = sum(1 for t in today_trades if t.get('status') == 'win')
                losses = sum(1 for t in today_trades if t.get('status') == 'loss')
                win_rate = (wins / len(today_trades) * 100) if today_trades else 0
                
                summary += f"✅ Wins: {wins} | ❌ Losses: {losses} | 📈 Win Rate: {win_rate:.1f}%\n\n"
                
                for trade in today_trades[-5:]:  # Show last 5 trades
                    status_emoji = "✅" if trade.get('status') == 'win' else "❌"
                    summary += f"{status_emoji} <b>{trade['symbol']}</b> {trade['direction']} - {trade.get('status', 'unknown')}\n"
            else:
                summary += "No completed trades today\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating forex summary: {e}")
            return f"❌ Error generating forex summary: {e}"
    
    def get_stock_uk_market_close_summary(self) -> str:
        """Generate UK market close summary for stock bot"""
        try:
            # Load active stock trades (gracefully handle missing file)
            try:
                with open('active_trades.json', 'r') as f:
                    active_trades = json.load(f)
            except FileNotFoundError:
                logger.warning("⚠️ active_trades.json not found - treating as no active trades")
                active_trades = []
            
            # Filter UK trades
            uk_trades = [t for t in active_trades if t.get('market') == 'UK']
            
            ldn_now = datetime.now(self.london_tz)
            uk_close_ldn = ldn_now.replace(hour=16, minute=30, second=0, microsecond=0)
            uk_close_dxb = uk_close_ldn.astimezone(self.dubai_tz)

            summary = f"""
🇬🇧 <b>UK STOCK MARKET CLOSE NOTIFICATION</b>
🕐 Time: {datetime.now(self.dubai_tz).strftime('%H:%M:%S')} Dubai
📅 Date: {datetime.now(self.dubai_tz).strftime('%Y-%m-%d')}

⚠️ <b>UK MARKET CLOSES IN 15 MINUTES!</b>
⏰ Close Time: {uk_close_dxb.strftime('%H:%M')} Dubai ({uk_close_ldn.strftime('%H:%M')} London)

📈 <b>ACTIVE UK TRADES ({len(uk_trades)})</b>
"""
            
            if uk_trades:
                summary += "Consider closing these positions before market close:\n\n"
                for trade in uk_trades:
                    direction_emoji = "🟢" if trade['direction'] == 'LONG' else "🔴"
                    summary += f"{direction_emoji} <b>{trade['symbol']}</b> {trade['direction']}\n"
                    summary += f"   Entry: {trade['entry']} | Stop: {trade['stop']} | Target: {trade['target']}\n"
                    summary += f"   R:R: {trade['risk_reward']:.1f}:1\n\n"
            else:
                summary += "No active UK trades\n"
            
            summary += "💡 <b>RECOMMENDATION:</b> Close all UK positions before 4:30 PM Dubai to avoid overnight risk"
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating UK summary: {e}")
            return f"❌ Error generating UK summary: {e}"
    
    def get_stock_us_early_warning(self) -> str:
        """Generate US early close warning for stock bot (10 PM Dubai)"""
        try:
            # Load active stock trades (gracefully handle missing file)
            try:
                with open('active_trades.json', 'r') as f:
                    active_trades = json.load(f)
            except FileNotFoundError:
                logger.warning("⚠️ active_trades.json not found - treating as no active trades")
                active_trades = []
            
            # Filter US trades
            us_trades = [t for t in active_trades if t.get('market') == 'US']
            
            ny_now = datetime.now(self.ny_tz)
            us_close_ny = ny_now.replace(hour=16, minute=0, second=0, microsecond=0)
            us_close_dxb = us_close_ny.astimezone(self.dubai_tz)
            time_to_close = us_close_dxb - datetime.now(self.dubai_tz)
            hours_to_close = time_to_close.total_seconds() / 3600

            summary = f"""
🇺🇸 <b>US MARKET EARLY WARNING</b>
🕐 Time: {datetime.now(self.dubai_tz).strftime('%H:%M:%S')} Dubai
📅 Date: {datetime.now(self.dubai_tz).strftime('%Y-%m-%d')}

⏰ <b>US MARKET CLOSES IN {hours_to_close:.1f} HOURS</b>
⏰ Close Time: {us_close_dxb.strftime('%H:%M')} Dubai ({us_close_ny.strftime('%H:%M')} New York)

📈 <b>ACTIVE US TRADES ({len(us_trades)})</b>
"""
            
            if us_trades:
                summary += "Review these positions before bed:\n\n"
                for trade in us_trades:
                    direction_emoji = "🟢" if trade['direction'] == 'LONG' else "🔴"
                    summary += f"{direction_emoji} <b>{trade['symbol']}</b> {trade['direction']}\n"
                    summary += f"   Entry: {trade['entry']} | Stop: {trade['stop']} | Target: {trade['target']}\n"
                    summary += f"   R:R: {trade['risk_reward']:.1f}:1\n\n"
            else:
                summary += "No active US trades\n"
            
            summary += "💡 <b>EARLY WARNING:</b> Consider your exit strategy before going to bed.\n"
            summary += "⏰ Final reminder will be sent at 12:45 AM Dubai (15 min before close)."
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating US early warning: {e}")
            return f"❌ Error generating US early warning: {e}"
    
    def get_stock_us_market_close_summary(self) -> str:
        """Generate US market close summary for stock bot (final warning)"""
        try:
            # Load active stock trades (gracefully handle missing file)
            try:
                with open('active_trades.json', 'r') as f:
                    active_trades = json.load(f)
            except FileNotFoundError:
                logger.warning("⚠️ active_trades.json not found - treating as no active trades")
                active_trades = []
            
            # Filter US trades
            us_trades = [t for t in active_trades if t.get('market') == 'US']
            
            ny_now = datetime.now(self.ny_tz)
            us_close_ny = ny_now.replace(hour=16, minute=0, second=0, microsecond=0)
            us_close_dxb = us_close_ny.astimezone(self.dubai_tz)

            summary = f"""
🇺🇸 <b>US MARKET FINAL CLOSE WARNING</b>
🕐 Time: {datetime.now(self.dubai_tz).strftime('%H:%M:%S')} Dubai
📅 Date: {datetime.now(self.dubai_tz).strftime('%Y-%m-%d')}

🚨 <b>US MARKET CLOSES IN 15 MINUTES!</b>
⏰ Close Time: {us_close_dxb.strftime('%H:%M')} Dubai ({us_close_ny.strftime('%H:%M')} New York)

📈 <b>ACTIVE US TRADES ({len(us_trades)})</b>
"""
            
            if us_trades:
                summary += "⚠️ FINAL CALL - Close these positions NOW:\n\n"
                for trade in us_trades:
                    direction_emoji = "🟢" if trade['direction'] == 'LONG' else "🔴"
                    summary += f"{direction_emoji} <b>{trade['symbol']}</b> {trade['direction']}\n"
                    summary += f"   Entry: {trade['entry']} | Stop: {trade['stop']} | Target: {trade['target']}\n"
                    summary += f"   R:R: {trade['risk_reward']:.1f}:1\n\n"
            else:
                summary += "No active US trades\n"
            
            summary += "🚨 <b>CRITICAL:</b> Market closes in 15 minutes - Close positions immediately!"
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating US summary: {e}")
            return f"❌ Error generating US summary: {e}"
    
    def is_uk_trading_day(self) -> bool:
        """Check if UK market is open today (not weekend or holiday)"""
        try:
            if not self.lse:
                # Fallback to weekend check only
                now_ldn = datetime.now(self.london_tz)
                return now_ldn.weekday() < 5
            
            # Get today's date in London timezone
            now_ldn = datetime.now(self.london_tz)
            today = now_ldn.date()
            
            # Check if market is open today
            schedule = self.lse.schedule(start_date=today, end_date=today)
            return len(schedule) > 0
            
        except Exception as e:
            logger.error(f"Error checking UK trading day: {e}")
            # Fallback to weekend check
            now_ldn = datetime.now(self.london_tz)
            return now_ldn.weekday() < 5
    
    def is_us_trading_day(self) -> bool:
        """Check if US market is open today (not weekend or holiday)"""
        try:
            if not self.nyse:
                # Fallback to weekend check only
                now_ny = datetime.now(self.ny_tz)
                return now_ny.weekday() < 5
            
            # Get today's date in NY timezone
            now_ny = datetime.now(self.ny_tz)
            today = now_ny.date()
            
            # Check if market is open today
            schedule = self.nyse.schedule(start_date=today, end_date=today)
            return len(schedule) > 0
            
        except Exception as e:
            logger.error(f"Error checking US trading day: {e}")
            # Fallback to weekend check
            now_ny = datetime.now(self.ny_tz)
            return now_ny.weekday() < 5
    
    def get_next_uk_holiday(self) -> str:
        """Get the next UK market holiday"""
        try:
            if not self.lse:
                return "Unknown"
            
            now_ldn = datetime.now(self.london_tz)
            # Check next 90 days
            end_date = now_ldn + timedelta(days=90)
            
            holidays = self.lse.holidays().holidays
            for holiday in holidays:
                if holiday > now_ldn.date():
                    return holiday.strftime('%Y-%m-%d')
            return "None in next 90 days"
        except:
            return "Unknown"
    
    def get_next_us_holiday(self) -> str:
        """Get the next US market holiday"""
        try:
            if not self.nyse:
                return "Unknown"
            
            now_ny = datetime.now(self.ny_tz)
            # Check next 90 days
            end_date = now_ny + timedelta(days=90)
            
            holidays = self.nyse.holidays().holidays
            for holiday in holidays:
                if holiday > now_ny.date():
                    return holiday.strftime('%Y-%m-%d')
            return "None in next 90 days"
        except:
            return "Unknown"
    
    def should_send_uk_open_notification(self) -> bool:
        """Check if it's time to send UK market open notification (12:00 PM Dubai)"""
        if not self.is_uk_trading_day():
            return False
        
        now_dubai = datetime.now(self.dubai_tz)
        return now_dubai.hour == 12 and 0 <= now_dubai.minute <= 5
    
    def should_send_us_open_notification(self) -> bool:
        """Check if it's time to send US market open notification (6:30 PM Dubai)"""
        if not self.is_us_trading_day():
            return False
        
        now_dubai = datetime.now(self.dubai_tz)
        return now_dubai.hour == 18 and 30 <= now_dubai.minute <= 35
    
    def get_stock_uk_market_open_notification(self) -> str:
        """Generate UK market open notification"""
        now_dubai = datetime.now(self.dubai_tz)
        now_london = datetime.now(self.london_tz)
        
        return f"""
🇬🇧 <b>UK STOCK MARKET OPEN</b>
🕐 Time: {now_dubai.strftime('%H:%M:%S')} Dubai ({now_london.strftime('%H:%M:%S')} London)
📅 Date: {now_dubai.strftime('%Y-%m-%d')}

✅ <b>UK MARKET IS NOW OPEN</b>

📊 <b>Monitoring 12 UK Stocks:</b>
LLOY.L, VOD.L, BARC.L, TSCO.L, BP.L, AZN.L, ULVR.L, SHEL.L, HSBA.L, RIO.L, DGE.L, GSK.L

⏰ <b>ORB Strategy Active:</b>
   Opening Range: 12:00-12:30 PM Dubai
   Trading Window: 12:30-3:00 PM Dubai (2.5 hours)

🔔 You'll receive ORB breakout signals if setups occur (2/4 confirmations required)
"""
    
    def get_stock_us_market_open_notification(self) -> str:
        """Generate US market open notification"""
        now_dubai = datetime.now(self.dubai_tz)
        now_ny = datetime.now(self.ny_tz)
        
        return f"""
🇺🇸 <b>US STOCK MARKET OPEN</b>
🕐 Time: {now_dubai.strftime('%H:%M:%S')} Dubai ({now_ny.strftime('%H:%M:%S')} New York)
📅 Date: {now_dubai.strftime('%Y-%m-%d')}

✅ <b>US MARKET IS NOW OPEN</b>

📊 <b>Monitoring 12 US Stocks:</b>
AAPL, TSLA, MSFT, GOOGL, AMZN, META, NVDA, NFLX, AMD, UBER, COIN, DIS

⏰ <b>ORB Strategy Active:</b>
   Opening Range: 6:30-7:00 PM Dubai
   Trading Window: 7:00-9:30 PM Dubai (2.5 hours)

🔔 You'll receive ORB breakout signals if setups occur (2/4 confirmations required)
"""
    
    def should_send_forex_summary(self) -> bool:
        """Check if it's time to send forex daily summary (9 PM Dubai)"""
        now = datetime.now(self.dubai_tz)
        return now.hour == 21 and now.minute == 0  # 9:00 PM Dubai
    
    def should_send_uk_close_notification(self) -> bool:
        """Check 15 minutes before UK close using London local time (DST-aware)"""
        # Check if it's a trading day first (blocks weekends and holidays)
        if not self.is_uk_trading_day():
            return False
        
        now_ldn = datetime.now(self.london_tz)
        return now_ldn.hour == 16 and now_ldn.minute == 15
    
    def should_send_us_early_warning(self) -> bool:
        """Check for early US close warning (10 PM Dubai - user still awake)"""
        # Check if it's a trading day first (blocks weekends and holidays)
        if not self.is_us_trading_day():
            return False
        
        now_dubai = datetime.now(self.dubai_tz)
        return now_dubai.hour == 22 and now_dubai.minute == 0  # 10:00 PM Dubai
    
    def should_send_us_close_notification(self) -> bool:
        """Check 15 minutes before US close using New York local time (DST-aware)"""
        # Check if it's a trading day first (blocks weekends and holidays)
        if not self.is_us_trading_day():
            return False
        
        now_ny = datetime.now(self.ny_tz)
        return now_ny.hour == 15 and now_ny.minute == 45
    
    def should_send_holiday_notification(self) -> bool:
        """Send holiday notification at 9 AM Dubai if market is closed"""
        now_dubai = datetime.now(self.dubai_tz)
        
        # Only send at 9:00 AM Dubai
        if now_dubai.hour != 9 or now_dubai.minute != 0:
            return False
        
        # Check if either market is closed for holiday/weekend
        uk_closed = not self.is_uk_trading_day()
        us_closed = not self.is_us_trading_day()
        
        return uk_closed or us_closed
    
    def get_holiday_notification(self) -> str:
        """Generate holiday notification message"""
        try:
            uk_trading = self.is_uk_trading_day()
            us_trading = self.is_us_trading_day()
            
            now_dubai = datetime.now(self.dubai_tz)
            
            summary = f"""
🏖️ <b>MARKET HOLIDAY NOTIFICATION</b>
📅 Date: {now_dubai.strftime('%Y-%m-%d')}
🕐 Time: {now_dubai.strftime('%H:%M')} Dubai

"""
            
            if not uk_trading:
                summary += "🇬🇧 <b>UK MARKET CLOSED</b> - Weekend/Holiday\n"
                next_uk = self.get_next_uk_holiday()
                summary += f"   Next UK holiday: {next_uk}\n\n"
            else:
                summary += "🇬🇧 UK Market: ✅ OPEN\n\n"
            
            if not us_trading:
                summary += "🇺🇸 <b>US MARKET CLOSED</b> - Weekend/Holiday\n"
                next_us = self.get_next_us_holiday()
                summary += f"   Next US holiday: {next_us}\n\n"
            else:
                summary += "🇺🇸 US Market: ✅ OPEN\n\n"
            
            summary += "💡 No stock trading signals will be sent today for closed markets."
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating holiday notification: {e}")
            return f"❌ Error generating holiday notification: {e}"
    
    def should_send_forex_open_trades_summary(self) -> bool:
        """Check if it's time to send forex open trades summary (8:30-8:45 PM Dubai window)"""
        now = datetime.now(self.dubai_tz)
        return now.hour == 20 and 30 <= now.minute <= 45
    
    def get_forex_open_trades_summary(self) -> str:
        """Generate detailed forex open trades summary with current status"""
        try:
            # Load active trades
            try:
                with open('active_trades.json', 'r') as f:
                    active_trades = json.load(f)
            except FileNotFoundError:
                logger.warning("⚠️ active_trades.json not found")
                active_trades = []
            
            if not active_trades:
                return f"""
📊 <b>FOREX OPEN TRADES SUMMARY</b>
🕐 Time: {datetime.now(self.dubai_tz).strftime('%H:%M:%S')} Dubai
📅 Date: {datetime.now(self.dubai_tz).strftime('%Y-%m-%d')}

No open trades currently.
"""
            
            # Import for price fetching
            from rate_limited_data_fetcher import RateLimitedDataFetcher
            fetcher = RateLimitedDataFetcher(base_delay=1.0)
            
            summary = f"""
📊 <b>FOREX OPEN TRADES SUMMARY</b>
🕐 Time: {datetime.now(self.dubai_tz).strftime('%H:%M:%S')} Dubai
📅 Date: {datetime.now(self.dubai_tz).strftime('%Y-%m-%d')}

💼 <b>Active Positions: {len(active_trades)}</b>

"""
            
            for trade in active_trades:
                symbol = trade['symbol']
                direction = trade['direction']
                entry = float(trade['entry'])
                stop = float(trade['stop'])
                target = float(trade['target'])
                
                # Get current price
                current_price = fetcher.get_current_price(symbol)
                if not current_price:
                    current_price = entry  # Fallback
                
                # Calculate progress
                if direction == 'LONG':
                    total_distance = target - entry
                    current_progress = current_price - entry
                else:  # SHORT
                    total_distance = entry - target
                    current_progress = entry - current_price
                
                # Calculate percentage to target
                progress_pct = (current_progress / total_distance * 100) if total_distance != 0 else 0
                progress_pct = max(0, min(100, progress_pct))  # Clamp between 0-100
                
                # Calculate P&L
                if direction == 'LONG':
                    pnl_pips = current_price - entry
                else:
                    pnl_pips = entry - current_price
                
                # Grade the trade
                if progress_pct >= 80:
                    grade = "🟢 EXCELLENT"
                elif progress_pct >= 50:
                    grade = "🟡 GOOD"
                elif progress_pct >= 20:
                    grade = "🟠 MODERATE"
                elif progress_pct > 0:
                    grade = "🔵 EARLY"
                else:
                    grade = "🔴 LOSING"
                
                direction_emoji = "🟢" if direction == 'LONG' else "🔴"
                
                summary += f"""
━━━━━━━━━━━━━━━━━━━━━━
{direction_emoji} <b>{symbol}</b> - {direction}
Entry: {entry:.5f}
Current: {current_price:.5f}
Stop Loss: {stop:.5f}
Take Profit: {target:.5f}
P&L: {pnl_pips:+.5f} pips
Progress: {progress_pct:.1f}% to target
Status: {grade}

"""
            
            summary += """━━━━━━━━━━━━━━━━━━━━━━
💡 Check your MT5 to verify these trades match your actual open positions."""
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating forex open trades summary: {e}")
            return f"❌ Error generating forex open trades summary: {e}"

def main():
    """Test the daily summary system"""
    # Load config
    try:
        from config import FOREX_TELEGRAM_BOT_TOKEN, FOREX_TELEGRAM_CHAT_ID
        summary_system = DailySummarySystem(FOREX_TELEGRAM_BOT_TOKEN, FOREX_TELEGRAM_CHAT_ID)
        
        # Test forex summary
        print("Testing forex daily summary...")
        forex_summary = summary_system.get_forex_daily_summary()
        print(forex_summary)
        
        # Test UK summary
        print("\nTesting UK market close summary...")
        uk_summary = summary_system.get_stock_uk_market_close_summary()
        print(uk_summary)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
