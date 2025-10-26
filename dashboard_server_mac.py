#!/usr/bin/env python3
"""
ZoneSync Trading Dashboard Server - macOS Compatible Version
Serves the performance tracking dashboard and handles outcome recording
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from flask import Flask, jsonify, request
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class DashboardManager:
    """Manages dashboard data and outcome recording"""

    def __init__(self):
        # Use local path for macOS
        self.base_path = Path(__file__).parent
        self.signals_file = self.base_path / "signals_history.json"
        self.dashboard_data = []
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
                logger.info(f"Loaded {len(self.dashboard_data)} signals")
            else:
                logger.warning(f"Signals file not found: {self.signals_file}")
                # Create empty file
                self.dashboard_data = []
                self.save_signals()
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
        """Record trade outcome for a signal"""
        try:
            signal = next((s for s in self.dashboard_data if s.get('signal_id') == signal_id), None)

            if not signal:
                logger.error(f"Signal not found: {signal_id}")
                return False

            signal['outcome'] = outcome
            signal['status'] = 'completed'
            signal['outcome_timestamp'] = datetime.now().isoformat()

            # Calculate PnL if not provided
            if pnl is None:
                if outcome == 'win':
                    # Assume full target hit
                    if signal.get('zone_type') == 'demand':
                        pnl = (signal['target'] - signal['entry']) * 10000  # Convert to pips
                    else:
                        pnl = (signal['entry'] - signal['target']) * 10000  # Convert to pips
                else:
                    # Assume full stop hit
                    if signal.get('zone_type') == 'demand':
                        pnl = (signal['stop'] - signal['entry']) * 10000  # Convert to pips (negative)
                    else:
                        pnl = (signal['entry'] - signal['stop']) * 10000  # Convert to pips (negative)

            signal['pnl'] = round(pnl, 2)

            self.save_signals()
            logger.info(f"Recorded {outcome} for signal {signal_id} with P&L: {pnl}")
            return True

        except Exception as e:
            logger.error(f"Error recording outcome: {e}")
            return False

    def calculate_performance_stats(self) -> Dict[str, Any]:
        """Calculate performance statistics"""
        completed_trades = [s for s in self.dashboard_data if s.get('outcome')]

        if not completed_trades:
            return {
                'win_rate': 0,
                'total_trades': 0,
                'total_signals': len(self.dashboard_data),
                'net_pnl': 0,
                'wins': 0,
                'losses': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'current_streak': 0,
                'streak_type': None
            }

        wins = [t for t in completed_trades if t['outcome'] == 'win']
        losses = [t for t in completed_trades if t['outcome'] == 'loss']

        win_rate = (len(wins) / len(completed_trades)) * 100

        # Calculate P&L as percentage (Risk/Reward based)
        total_r = 0
        for trade in completed_trades:
            if trade['outcome'] == 'win':
                rr = trade.get('risk_reward', 2.0)
                total_r += rr
            else:
                total_r -= 1.0

        net_pnl_percentage = total_r * 100 / len(completed_trades) if completed_trades else 0
        avg_win_r = sum(t.get('risk_reward', 2.0) for t in wins) / len(wins) if wins else 0
        avg_loss_r = -1.0

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
            'net_pnl_percentage': round(net_pnl_percentage, 1),
            'total_r': round(total_r, 2),
            'wins': len(wins),
            'losses': len(losses),
            'avg_win_r': round(avg_win_r, 1),
            'avg_loss_r': avg_loss_r,
            'current_streak': streak,
            'streak_type': streak_type
        }

# Initialize dashboard manager
dashboard_manager = DashboardManager()

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    try:
        # Try new modern dashboard first
        dashboard_html_path = Path(__file__).parent / 'trading_dashboard_v2.html'
        if not dashboard_html_path.exists():
            # Fallback to old dashboard
            dashboard_html_path = Path(__file__).parent / 'trading_dashboard.html'
        
        with open(dashboard_html_path, 'r') as f:
            dashboard_html = f.read()
        return dashboard_html
    except FileNotFoundError:
        return '''
        <h1>Dashboard Not Found</h1>
        <p>Please ensure trading_dashboard_v2.html is in the same directory.</p>
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

@app.route('/api/trades')
def get_trades():
    """API endpoint to get all trades with $10 risk"""
    try:
        trades_file = Path(__file__).parent / "trades_history.json"
        if trades_file.exists():
            with open(trades_file, 'r') as f:
                trades = json.load(f)
            return jsonify(trades)
        return jsonify([])
    except Exception as e:
        logger.error(f"Error in get_trades: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade_stats')
def get_trade_stats():
    """API endpoint to get trade statistics with $10 risk"""
    try:
        trades_file = Path(__file__).parent / "trades_history.json"
        if trades_file.exists():
            with open(trades_file, 'r') as f:
                trades = json.load(f)
            
            completed = [t for t in trades if t['status'] in ['win', 'loss', 'breakeven']]
            active = [t for t in trades if t['status'] == 'active']
            wins = [t for t in trades if t['status'] == 'win']
            losses = [t for t in trades if t['status'] == 'loss']
            
            stats = {
                'total_trades': len(trades),
                'completed_trades': len(completed),
                'active_trades': len(active),
                'wins': len(wins),
                'losses': len(losses),
                'win_rate': (len(wins) / len(completed) * 100) if completed else 0,
                'total_pnl': sum(t['pnl'] for t in completed),
                'average_rr': sum(t['risk_reward'] for t in trades) / len(trades) if trades else 0,
                'total_risk_deployed': len(active) * 10.00,
                'risk_per_trade': 10.00
            }
            
            return jsonify(stats)
        return jsonify({'total_trades': 0})
    except Exception as e:
        logger.error(f"Error in get_trade_stats: {e}")
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
        'signals_loaded': len(dashboard_manager.dashboard_data)
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
    logger.info("Starting ZoneSync Trading Dashboard Server (macOS)...")
    logger.info("Dashboard will be available at:")
    logger.info("  - Local: http://localhost:5000")
    logger.info("  - Network: http://84.235.245.60:5000")

    # Start auto-refresh thread
    refresh_thread = threading.Thread(target=auto_refresh_data, daemon=True)
    refresh_thread.start()

    # Run the Flask app on port 5000 with better network config
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    run_dashboard_server()

