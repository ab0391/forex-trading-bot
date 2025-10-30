#!/usr/bin/env python3
"""
Daily Summary System for Trading Bots
Provides end-of-day summaries and market close notifications
"""

import json
import logging
import requests
from datetime import datetime, time
import pytz
from typing import List, Dict, Any

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
    
    def get_stock_us_market_close_summary(self) -> str:
        """Generate US market close summary for stock bot"""
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
🇺🇸 <b>US STOCK MARKET CLOSE NOTIFICATION</b>
🕐 Time: {datetime.now(self.dubai_tz).strftime('%H:%M:%S')} Dubai
📅 Date: {datetime.now(self.dubai_tz).strftime('%Y-%m-%d')}

⚠️ <b>US MARKET CLOSES IN 15 MINUTES!</b>
⏰ Close Time: {us_close_dxb.strftime('%H:%M')} Dubai ({us_close_ny.strftime('%H:%M')} New York)

📈 <b>ACTIVE US TRADES ({len(us_trades)})</b>
"""
            
            if us_trades:
                summary += "Consider closing these positions before market close:\n\n"
                for trade in us_trades:
                    direction_emoji = "🟢" if trade['direction'] == 'LONG' else "🔴"
                    summary += f"{direction_emoji} <b>{trade['symbol']}</b> {trade['direction']}\n"
                    summary += f"   Entry: {trade['entry']} | Stop: {trade['stop']} | Target: {trade['target']}\n"
                    summary += f"   R:R: {trade['risk_reward']:.1f}:1\n\n"
            else:
                summary += "No active US trades\n"
            
            summary += "💡 <b>RECOMMENDATION:</b> Close all US positions before 1:00 AM Dubai to avoid overnight risk"
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating US summary: {e}")
            return f"❌ Error generating US summary: {e}"
    
    def should_send_forex_summary(self) -> bool:
        """Check if it's time to send forex daily summary (9 PM Dubai)"""
        now = datetime.now(self.dubai_tz)
        return now.hour == 21 and now.minute == 0  # 9:00 PM Dubai
    
    def should_send_uk_close_notification(self) -> bool:
        """Check 15 minutes before UK close using London local time (DST-aware)"""
        now_ldn = datetime.now(self.london_tz)
        return now_ldn.hour == 16 and now_ldn.minute == 15
    
    def should_send_us_close_notification(self) -> bool:
        """Check 15 minutes before US close using New York local time (DST-aware)"""
        now_ny = datetime.now(self.ny_tz)
        return now_ny.hour == 15 and now_ny.minute == 45

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
