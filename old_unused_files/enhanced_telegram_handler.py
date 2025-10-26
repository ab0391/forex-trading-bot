#!/usr/bin/env python3
"""
Enhanced Telegram Handler for ZoneSync Bot
Adds outcome recording shortcuts and dashboard integration
"""

import os
import json
import logging
import requests
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramOutcomeHandler:
    """Handles Telegram shortcuts for recording trade outcomes"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.signals_file = Path("/home/ubuntu/fxbot/signals_history.json")
        self.last_update_id = 0

    def process_telegram_messages(self):
        """Check for new Telegram messages and process outcome commands"""
        if not self.bot_token:
            return

        try:
            # Get updates from Telegram
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 1}

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            updates = response.json()

            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    self.last_update_id = update["update_id"]
                    self.process_update(update)

        except Exception as e:
            logger.error(f"Error processing Telegram messages: {e}")

    def process_update(self, update: Dict):
        """Process a single Telegram update"""
        try:
            message = update.get("message", {})
            text = message.get("text", "").strip()
            chat_id = message.get("chat", {}).get("id")

            # Only process messages from authorized chat
            if str(chat_id) != str(self.chat_id):
                return

            # Process outcome commands
            if self.is_outcome_command(text):
                self.handle_outcome_command(text)

        except Exception as e:
            logger.error(f"Error processing update: {e}")

    def is_outcome_command(self, text: str) -> bool:
        """Check if message is an outcome recording command"""
        patterns = [
            r'^[✅❌]\s*[A-Z]{6}$',  # ✅ EURUSD or ❌ GBPUSD
            r'^(win|loss|w|l)\s+[A-Z]{6}$',  # win EURUSD or loss GBPUSD
            r'^[A-Z]{6}\s+[✅❌]$',  # EURUSD ✅ or GBPUSD ❌
            r'^[A-Z]{6}\s+(win|loss|w|l)$',  # EURUSD win or GBPUSD loss
        ]

        text_upper = text.upper()
        return any(re.match(pattern, text_upper) for pattern in patterns)

    def handle_outcome_command(self, text: str):
        """Handle outcome recording command"""
        try:
            text_upper = text.upper()

            # Parse the command
            outcome = None
            symbol = None

            if '✅' in text or 'WIN' in text_upper or text_upper.startswith('W '):
                outcome = 'win'
            elif '❌' in text or 'LOSS' in text_upper or text_upper.startswith('L '):
                outcome = 'loss'

            # Extract symbol
            symbol_match = re.search(r'[A-Z]{6}', text_upper)
            if symbol_match:
                symbol = symbol_match.group()

            if outcome and symbol:
                success = self.record_outcome_for_symbol(symbol, outcome)
                if success:
                    self.send_confirmation(symbol, outcome)
                else:
                    self.send_error_message(f"Could not find active signal for {symbol}")

        except Exception as e:
            logger.error(f"Error handling outcome command: {e}")
            self.send_error_message("Error processing outcome command")

    def record_outcome_for_symbol(self, symbol: str, outcome: str) -> bool:
        """Record outcome for the most recent active signal of a symbol"""
        try:
            # Load signals
            signals = self.load_signals()

            # Find the most recent active signal for this symbol
            active_signals = [
                s for s in signals
                if s.get('symbol') == symbol and s.get('status') == 'active'
            ]

            if not active_signals:
                logger.warning(f"No active signals found for {symbol}")
                return False

            # Take the most recent one
            signal = sorted(active_signals, key=lambda x: x.get('timestamp', ''), reverse=True)[0]

            # Update the signal
            signal['outcome'] = outcome
            signal['status'] = 'completed'
            signal['outcome_timestamp'] = datetime.now().isoformat()

            # Calculate PnL
            pnl = self.calculate_pnl(signal, outcome)
            signal['pnl'] = pnl

            # Save back
            self.save_signals(signals)

            logger.info(f"Recorded {outcome} for {symbol}: {signal['signal_id']}")
            return True

        except Exception as e:
            logger.error(f"Error recording outcome for {symbol}: {e}")
            return False

    def calculate_pnl(self, signal: Dict, outcome: str) -> float:
        """Calculate P&L for a signal based on outcome"""
        try:
            entry = signal.get('entry', 0)
            target = signal.get('target', 0)
            stop = signal.get('stop', 0)
            zone_type = signal.get('zone_type', 'demand')

            if outcome == 'win':
                if zone_type == 'demand':
                    pnl = (target - entry) * 10000  # Convert to pips
                else:  # supply
                    pnl = (entry - target) * 10000  # Convert to pips
            else:  # loss
                if zone_type == 'demand':
                    pnl = (stop - entry) * 10000  # Convert to pips (negative)
                else:  # supply
                    pnl = (entry - stop) * 10000  # Convert to pips (negative)

            return round(pnl, 2)

        except Exception as e:
            logger.error(f"Error calculating P&L: {e}")
            return 0.0

    def load_signals(self) -> List[Dict]:
        """Load signals from JSON file"""
        try:
            if self.signals_file.exists():
                with open(self.signals_file, 'r') as f:
                    signals = json.load(f)
                    if isinstance(signals, dict):
                        signals = list(signals.values()) if signals else []
                    return signals
            return []
        except Exception as e:
            logger.error(f"Error loading signals: {e}")
            return []

    def save_signals(self, signals: List[Dict]):
        """Save signals to JSON file"""
        try:
            with open(self.signals_file, 'w') as f:
                json.dump(signals, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving signals: {e}")

    def send_confirmation(self, symbol: str, outcome: str):
        """Send confirmation message for recorded outcome"""
        emoji = "✅" if outcome == "win" else "❌"
        message = f"{emoji} *Outcome Recorded*\n\n📊 *{symbol}*: {outcome.upper()}\n⏰ {datetime.now().strftime('%H:%M:%S')}"

        self.send_message(message)

    def send_error_message(self, error: str):
        """Send error message"""
        message = f"❌ *Error*\n\n{error}"
        self.send_message(message)

    def send_message(self, message: str):
        """Send message to Telegram"""
        if not self.bot_token or not self.chat_id:
            return

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")

    def send_performance_summary(self):
        """Send daily performance summary"""
        try:
            signals = self.load_signals()
            stats = self.calculate_stats(signals)

            if stats['total_trades'] == 0:
                return

            message = f"""
📊 *Daily Performance Summary*

🎯 *Win Rate:* {stats['win_rate']:.1f}%
📈 *Trades:* {stats['total_trades']} completed
💰 *P&L:* ${stats['net_pnl']:+.0f}
🔥 *Streak:* {stats['streak_type']}{stats['current_streak']}

📋 *Today's Results:*
• Wins: {stats['wins']}
• Losses: {stats['losses']}
• Avg Win: ${stats['avg_win']:+.0f}
• Avg Loss: ${stats['avg_loss']:+.0f}

Keep tracking your progress! 🚀
            """.strip()

            self.send_message(message)

        except Exception as e:
            logger.error(f"Error sending performance summary: {e}")

    def calculate_stats(self, signals: List[Dict]) -> Dict:
        """Calculate performance statistics"""
        completed_trades = [s for s in signals if s.get('outcome')]

        if not completed_trades:
            return {'total_trades': 0}

        wins = [t for t in completed_trades if t['outcome'] == 'win']
        losses = [t for t in completed_trades if t['outcome'] == 'loss']

        win_rate = (len(wins) / len(completed_trades)) * 100
        net_pnl = sum(t.get('pnl', 0) for t in completed_trades)

        # Calculate streak
        streak = 0
        streak_type = ''
        for trade in reversed(completed_trades):
            if streak == 0:
                streak_type = 'W' if trade['outcome'] == 'win' else 'L'
                streak = 1
            elif (trade['outcome'] == 'win' and streak_type == 'W') or \
                 (trade['outcome'] == 'loss' and streak_type == 'L'):
                streak += 1
            else:
                break

        return {
            'win_rate': win_rate,
            'total_trades': len(completed_trades),
            'wins': len(wins),
            'losses': len(losses),
            'net_pnl': net_pnl,
            'avg_win': sum(t.get('pnl', 0) for t in wins) / len(wins) if wins else 0,
            'avg_loss': sum(t.get('pnl', 0) for t in losses) / len(losses) if losses else 0,
            'current_streak': streak,
            'streak_type': streak_type
        }

# Convenience function for integration with main bot
def process_telegram_outcomes():
    """Process Telegram outcome commands (called by main bot)"""
    try:
        handler = TelegramOutcomeHandler()
        handler.process_telegram_messages()
    except Exception as e:
        logger.error(f"Error in process_telegram_outcomes: {e}")

if __name__ == "__main__":
    # Test the Telegram handler
    logging.basicConfig(level=logging.INFO)

    handler = TelegramOutcomeHandler()
    print("Testing Telegram outcome handler...")
    print("Send messages like:")
    print("  ✅ EURUSD")
    print("  ❌ GBPUSD")
    print("  win AUDUSD")
    print("  loss USDJPY")

    # Process messages for 30 seconds
    import time
    end_time = time.time() + 30

    while time.time() < end_time:
        handler.process_telegram_messages()
        time.sleep(2)

    print("Test completed")