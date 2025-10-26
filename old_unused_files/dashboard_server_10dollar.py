#!/usr/bin/env python3
"""
ZoneSync Trading Dashboard Server - $10 Trade Template
Serves the performance tracking dashboard with fixed $10 trade size
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from flask import Flask, render_template_string, jsonify, request, send_from_directory
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class DashboardManager:
    """Manages dashboard data with $10 trade template"""

    def __init__(self):
        self.signals_file = Path("/home/ubuntu/fxbot/signals_history.json")
        self.dashboard_data = {}
        self.load_signals()

    def load_signals(self):
        """Load signals from JSON file"""
        try:
            if self.signals_file.exists():
                with open(self.signals_file, 'r') as f:
                    signals = json.load(f)
                    # Convert to list if it's not already
                    if isinstance(signals, dict):
                        signals = list(signals.values()) if signals else []
                    self.dashboard_data = signals
            else:
                logger.warning(f"Signals file not found: {self.signals_file}")
                self.dashboard_data = []
        except Exception as e:
            logger.error(f"Error loading signals: {e}")
            self.dashboard_data = []

    def save_signals(self):
        """Save signals back to JSON file"""
        try:
            with open(self.signals_file, 'w') as f:
                json.dump(self.dashboard_data, f, indent=2)
            logger.info("Signals saved successfully")
        except Exception as e:
            logger.error(f"Error saving signals: {e}")

    def get_signals(self) -> List[Dict[str, Any]]:
        """Get all signals for dashboard"""
        self.load_signals()  # Refresh data
        return self.dashboard_data

    def record_outcome(self, signal_id: str, outcome: str, pnl: float = None) -> bool:
        """Record trade outcome with $10 trade template"""
        try:
            signal = next((s for s in self.dashboard_data if s.get('signal_id') == signal_id), None)

            if not signal:
                logger.error(f"Signal not found: {signal_id}")
                return False

            signal['outcome'] = outcome
            signal['status'] = 'completed'
            signal['outcome_timestamp'] = datetime.now().isoformat()

            # $10 Trade Template P&L Calculation
            if outcome == 'win':
                # Win: $10 × Risk/Reward ratio
                risk_reward = signal.get('risk_reward', 2.0)
                pnl_dollars = 10.0 * risk_reward
                logger.info(f"WIN: ${pnl_dollars:.2f} (Risk/Reward: {risk_reward}:1)")
            else:
                # Loss: Always -$10
                pnl_dollars = -10.0
                logger.info(f"LOSS: -$10.00")

            signal['pnl_dollars'] = pnl_dollars

            self.save_signals()
            logger.info(f"Recorded {outcome} for signal {signal_id} with P&L: ${pnl_dollars:.2f}")
            return True

        except Exception as e:
            logger.error(f"Error recording outcome: {e}")
            return False

    def calculate_performance_stats(self) -> Dict[str, Any]:
        """Calculate performance statistics with $10 trade template"""
        completed_trades = [s for s in self.dashboard_data if s.get('outcome')]

        if not completed_trades:
            return {
                'win_rate': 0,
                'total_trades': 0,
                'total_signals': len(self.dashboard_data),
                'net_pnl_dollars': 0,
                'account_balance': 0,
                'wins': 0,
                'losses': 0,
                'avg_win_dollars': 0,
                'avg_loss_dollars': -10,
                'current_streak': 0,
                'streak_type': None,
                'largest_win': 0,
                'largest_loss': -10
            }

        wins = [t for t in completed_trades if t['outcome'] == 'win']
        losses = [t for t in completed_trades if t['outcome'] == 'loss']

        win_rate = (len(wins) / len(completed_trades)) * 100

        # Calculate P&L in dollars using $10 trade template
        total_pnl_dollars = 0
        for trade in completed_trades:
            if trade['outcome'] == 'win':
                risk_reward = trade.get('risk_reward', 2.0)
                trade_pnl = 10.0 * risk_reward
            else:
                trade_pnl = -10.0

            # Store calculated P&L if not already stored
            if 'pnl_dollars' not in trade:
                trade['pnl_dollars'] = trade_pnl

            total_pnl_dollars += trade_pnl

        # Account balance starts at $0, so balance = total P&L
        account_balance = total_pnl_dollars

        # Calculate averages
        avg_win_dollars = sum(t.get('pnl_dollars', 10 * t.get('risk_reward', 2.0)) for t in wins) / len(wins) if wins else 0
        avg_loss_dollars = -10.0  # Always -$10 for losses

        # Find largest win/loss
        largest_win = max((t.get('pnl_dollars', 10 * t.get('risk_reward', 2.0)) for t in wins), default=0)
        largest_loss = -10.0  # Always -$10 for losses

        # Calculate current streak
        streak = 0
        streak_type = None
        for trade in reversed(completed_trades):
            if streak == 0:
                streak_type = trade['outcome']
                streak = 1
            elif trade['outcome'] == streak_type:
                streak += 1
            else:
                break

        return {
            'win_rate': round(win_rate, 1),
            'total_trades': len(completed_trades),
            'total_signals': len(self.dashboard_data),
            'net_pnl_dollars': round(total_pnl_dollars, 2),
            'account_balance': round(account_balance, 2),
            'wins': len(wins),
            'losses': len(losses),
            'avg_win_dollars': round(avg_win_dollars, 2),
            'avg_loss_dollars': avg_loss_dollars,
            'current_streak': streak,
            'streak_type': streak_type,
            'largest_win': round(largest_win, 2),
            'largest_loss': largest_loss
        }

# Initialize dashboard manager
dashboard_manager = DashboardManager()

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    try:
        with open('/home/ubuntu/fxbot/trading_dashboard.html', 'r') as f:
            dashboard_html = f.read()
        return dashboard_html
    except FileNotFoundError:
        return '''
        <h1>Dashboard Not Found</h1>
        <p>Please ensure trading_dashboard.html is in the /home/ubuntu/fxbot/ directory.</p>
        <p>You can access the API directly at <a href="/api/signals">/api/signals</a></p>
        '''

@app.route('/api/signals')
def get_signals():
    """API endpoint to get all signals"""
    try:
        signals = dashboard_manager.get_signals()
        return jsonify(signals)
    except Exception as e:
        logger.error(f"Error in get_signals: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get performance statistics"""
    try:
        stats = dashboard_manager.calculate_performance_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/record', methods=['POST'])
def record_outcome():
    """API endpoint to record trade outcome"""
    try:
        data = request.get_json()
        signal_id = data.get('signal_id')
        outcome = data.get('outcome')
        pnl = data.get('pnl')

        if not signal_id or not outcome:
            return jsonify({'error': 'Missing signal_id or outcome'}), 400

        if outcome not in ['win', 'loss']:
            return jsonify({'error': 'Outcome must be win or loss'}), 400

        success = dashboard_manager.record_outcome(signal_id, outcome, pnl)

        if success:
            return jsonify({'success': True, 'message': f'Recorded {outcome} for {signal_id}'})
        else:
            return jsonify({'error': 'Failed to record outcome'}), 500

    except Exception as e:
        logger.error(f"Error in record_outcome: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'signals_loaded': len(dashboard_manager.dashboard_data),
        'trade_template': '$10 fixed risk per trade'
    })

# Simple outcome recording endpoints for easy access
@app.route('/win/<signal_id>')
def record_win(signal_id):
    """Quick endpoint to record a win"""
    success = dashboard_manager.record_outcome(signal_id, 'win')
    return jsonify({'success': success, 'outcome': 'win', 'signal_id': signal_id})

@app.route('/loss/<signal_id>')
def record_loss(signal_id):
    """Quick endpoint to record a loss"""
    success = dashboard_manager.record_outcome(signal_id, 'loss')
    return jsonify({'success': success, 'outcome': 'loss', 'signal_id': signal_id})

def auto_refresh_data():
    """Automatically refresh dashboard data every minute"""
    while True:
        try:
            dashboard_manager.load_signals()
            time.sleep(60)  # Refresh every minute
        except Exception as e:
            logger.error(f"Error in auto_refresh: {e}")
            time.sleep(60)

def run_dashboard_server():
    """Run the dashboard server"""
    logger.info("Starting ZoneSync Trading Dashboard Server with $10 Trade Template...")

    # Start auto-refresh thread
    refresh_thread = threading.Thread(target=auto_refresh_data, daemon=True)
    refresh_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=80, debug=False)

if __name__ == '__main__':
    run_dashboard_server()