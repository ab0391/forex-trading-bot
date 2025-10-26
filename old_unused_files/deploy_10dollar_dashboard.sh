#!/bin/bash
# Deploy $10 Trade Template Dashboard

echo "💰 Deploying $10 Trade Template Dashboard"
echo "========================================"

# Upload updated dashboard server
scp dashboard_server_10dollar.py fxbot:/home/ubuntu/fxbot/

# SSH and deploy
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot

echo "🛑 Stopping dashboard service..."
sudo systemctl stop fxbot-dashboard.service

echo "📦 Backing up current dashboard server..."
cp dashboard_server.py dashboard_server_backup.py

echo "💰 Deploying $10 trade template dashboard..."
cp dashboard_server_10dollar.py dashboard_server.py

echo "🎨 Creating updated dashboard HTML with $10 template..."
cat > trading_dashboard.html << 'DASHBOARD_EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZoneSync Trading Dashboard - $10 Trade Template</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: #ffffff;
            height: 100%;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            min-height: calc(100vh - 40px);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }

        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            margin: 5px 0;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(255, 255, 255, 0.1);
            transition: transform 0.3s ease;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 8px;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .stat-label {
            font-size: 1.1em;
            opacity: 0.8;
            font-weight: 500;
        }

        .charts-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        .chart-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(255, 255, 255, 0.1);
            height: 350px;
            display: flex;
            flex-direction: column;
        }

        .chart-title {
            font-size: 1.3em;
            margin-bottom: 15px;
            text-align: center;
            font-weight: 600;
        }

        .chart-wrapper {
            flex: 1;
            position: relative;
            min-height: 250px;
        }

        .signals-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(255, 255, 255, 0.1);
            max-height: 500px;
            overflow-y: auto;
        }

        .signals-section h3 {
            margin-bottom: 20px;
            font-size: 1.4em;
            font-weight: 600;
        }

        .signal-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
            transition: all 0.3s ease;
            min-height: 70px;
        }

        .signal-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }

        .signal-pending {
            border-left-color: #ff9800;
        }

        .signal-info {
            flex: 1;
        }

        .signal-info strong {
            font-size: 1.1em;
            color: #4CAF50;
        }

        .signal-details {
            margin: 5px 0;
            font-size: 0.95em;
            opacity: 0.9;
        }

        .signal-timestamp {
            font-size: 0.85em;
            opacity: 0.7;
        }

        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            margin: 0 5px;
            transition: all 0.3s ease;
            font-size: 0.9em;
            white-space: nowrap;
        }

        .btn-win {
            background: #4CAF50;
            color: white;
        }

        .btn-loss {
            background: #f44336;
            color: white;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .refresh-info {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            font-size: 0.9em;
            opacity: 0.8;
        }

        .clean-slate {
            text-align: center;
            padding: 40px 20px;
            opacity: 0.7;
        }

        .clean-slate h4 {
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #4CAF50;
        }

        .clean-slate p {
            margin: 8px 0;
            font-size: 1.05em;
        }

        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            .charts-section {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 15px;
            }

            .stat-value {
                font-size: 1.8em;
            }

            .header h1 {
                font-size: 1.8em;
            }

            .chart-container {
                height: 300px;
            }

            .signal-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
                min-height: auto;
            }

            .signal-buttons {
                align-self: stretch;
                display: flex;
                gap: 10px;
            }

            .btn {
                flex: 1;
            }
        }

        /* Positive/Negative P&L coloring */
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        .neutral { color: #ffffff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 ZoneSync Trading Dashboard</h1>
            <p>$10 Trade Template - Real Dollar Tracking</p>
            <p><strong>Risk:</strong> $10 per trade | <strong>Rewards:</strong> Based on R:R ratio</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="winRate">0%</div>
                <div class="stat-label">Win Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalTrades">0</div>
                <div class="stat-label">Total Trades</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="accountBalance">$0</div>
                <div class="stat-label">Account Balance</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="netPnl">$0</div>
                <div class="stat-label">Total P&L</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="currentStreak">-</div>
                <div class="stat-label">Current Streak</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avgWin">$0</div>
                <div class="stat-label">Avg Win</div>
            </div>
        </div>

        <div class="charts-section">
            <div class="chart-container">
                <div class="chart-title">Win Rate Trend</div>
                <div class="chart-wrapper">
                    <canvas id="winRateChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <div class="chart-title">P&L Progress ($)</div>
                <div class="chart-wrapper">
                    <canvas id="pnlChart"></canvas>
                </div>
            </div>
        </div>

        <div class="signals-section">
            <h3>Recent Signals</h3>
            <div id="signalsList">
                <div class="clean-slate">
                    <h4>🎉 Clean Slate!</h4>
                    <p>Ready for enhanced bot with $10 trade template</p>
                    <p><strong>Win:</strong> $10 × R:R ratio | <strong>Loss:</strong> -$10</p>
                    <p>Example: 3:1 win = +$30, Loss = -$10</p>
                </div>
            </div>
        </div>

        <div class="refresh-info">
            <p>💰 $10 fixed risk per trade | Auto-refreshes every 60 seconds</p>
            <p id="lastUpdate">Last updated: Never (Fresh start)</p>
        </div>
    </div>

    <script>
        // Global chart variables
        let winRateChart = null;
        let pnlChart = null;

        function initializeCharts() {
            // Destroy existing charts if they exist
            if (winRateChart) {
                winRateChart.destroy();
            }
            if (pnlChart) {
                pnlChart.destroy();
            }

            // Win Rate Trend Chart
            const winRateCtx = document.getElementById('winRateChart').getContext('2d');
            winRateChart = new Chart(winRateCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Win Rate %',
                        data: [],
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.3,
                        fill: true,
                        pointBackgroundColor: '#4CAF50',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                color: '#ffffff',
                                callback: function(value) {
                                    return value + '%';
                                }
                            },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });

            // P&L Progress Chart
            const pnlCtx = document.getElementById('pnlChart').getContext('2d');
            pnlChart = new Chart(pnlCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Account Balance ($)',
                        data: [],
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.3,
                        fill: true,
                        pointBackgroundColor: '#2196F3',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            ticks: {
                                color: '#ffffff',
                                callback: function(value) {
                                    return '$' + value;
                                }
                            },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }

        function updateStats(stats) {
            document.getElementById('winRate').textContent = stats.win_rate + '%';
            document.getElementById('totalTrades').textContent = stats.total_trades;

            // Account balance
            const balanceElement = document.getElementById('accountBalance');
            balanceElement.textContent = '$' + stats.account_balance;
            balanceElement.className = stats.account_balance >= 0 ? 'positive' : 'negative';

            // Net P&L
            const pnlElement = document.getElementById('netPnl');
            const pnlText = (stats.net_pnl_dollars >= 0 ? '+' : '') + '$' + stats.net_pnl_dollars;
            pnlElement.textContent = pnlText;
            pnlElement.className = stats.net_pnl_dollars >= 0 ? 'positive' : 'negative';

            // Average win
            document.getElementById('avgWin').textContent = '$' + stats.avg_win_dollars;

            // Current streak
            if (stats.current_streak > 0) {
                const streakType = stats.streak_type === 'win' ? 'W' : 'L';
                const streakColor = stats.streak_type === 'win' ? 'positive' : 'negative';
                const streakElement = document.getElementById('currentStreak');
                streakElement.textContent = streakType + stats.current_streak;
                streakElement.className = streakColor;
            } else {
                const streakElement = document.getElementById('currentStreak');
                streakElement.textContent = '-';
                streakElement.className = 'neutral';
            }
        }

        function updateSignals(signals) {
            const signalsList = document.getElementById('signalsList');

            if (signals.length === 0) {
                signalsList.innerHTML = `
                    <div class="clean-slate">
                        <h4>🎉 Clean Slate!</h4>
                        <p>Ready for enhanced bot with $10 trade template</p>
                        <p><strong>Win:</strong> $10 × R:R ratio | <strong>Loss:</strong> -$10</p>
                        <p>Example: 3:1 win = +$30, Loss = -$10</p>
                    </div>
                `;
                return;
            }

            // Show recent signals (last 15)
            const recentSignals = signals.slice(-15).reverse();
            signalsList.innerHTML = recentSignals.map(signal => {
                const statusClass = signal.outcome ? '' : 'signal-pending';

                let outcomeButtons;
                if (signal.outcome) {
                    const rr = signal.risk_reward || 2;
                    const pnlAmount = signal.outcome === 'win' ? (10 * rr) : -10;
                    const pnlText = signal.outcome === 'win' ? `+$${pnlAmount}` : '-$10';
                    const pnlColor = signal.outcome === 'win' ? '#4CAF50' : '#f44336';

                    outcomeButtons = `<span style="color: ${pnlColor}; font-weight: bold;">
                        ${signal.outcome === 'win' ? '✅' : '❌'} ${signal.outcome.toUpperCase()}
                        ${pnlText}
                    </span>`;
                } else {
                    const rr = signal.risk_reward || 2;
                    const winAmount = 10 * rr;

                    outcomeButtons = `<div class="signal-buttons">
                        <button class="btn btn-win" onclick="recordOutcome('${signal.signal_id}', 'win')" title="Win: +$${winAmount}">✅ Win (+$${winAmount})</button>
                        <button class="btn btn-loss" onclick="recordOutcome('${signal.signal_id}', 'loss')" title="Loss: -$10">❌ Loss (-$10)</button>
                    </div>`;
                }

                return `
                    <div class="signal-item ${statusClass}">
                        <div class="signal-info">
                            <strong>${signal.symbol}</strong> ${signal.zone_type.toUpperCase()}
                            <div class="signal-details">Entry: ${signal.entry} | R:R: ${signal.risk_reward} | Risk: $10</div>
                            <div class="signal-timestamp">${new Date(signal.timestamp).toLocaleString()}</div>
                        </div>
                        ${outcomeButtons}
                    </div>
                `;
            }).join('');
        }

        async function fetchData() {
            try {
                const [statsResponse, signalsResponse] = await Promise.all([
                    fetch('/api/stats'),
                    fetch('/api/signals')
                ]);

                const stats = await statsResponse.json();
                const signals = await signalsResponse.json();

                updateStats(stats);
                updateSignals(signals);

                if (signals.length > 0) {
                    updateCharts(signals, stats);
                }

                document.getElementById('lastUpdate').textContent =
                    'Last updated: ' + new Date().toLocaleTimeString();

            } catch (error) {
                console.error('Error fetching data:', error);
                document.getElementById('lastUpdate').textContent =
                    'Last updated: Error fetching data';
            }
        }

        function updateCharts(signals, stats) {
            const completedTrades = signals.filter(s => s.outcome);

            if (completedTrades.length === 0) {
                return;
            }

            // Win rate trend
            const trendData = [];
            let wins = 0;
            let cumulativePnl = 0;

            completedTrades.forEach((signal, index) => {
                if (signal.outcome === 'win') {
                    wins++;
                    const rr = signal.risk_reward || 2;
                    cumulativePnl += (10 * rr);
                } else {
                    cumulativePnl -= 10;
                }

                const winRate = ((wins / (index + 1)) * 100).toFixed(1);
                const dateStr = new Date(signal.outcome_timestamp || signal.timestamp).toLocaleDateString();

                trendData.push({
                    date: dateStr,
                    winRate: parseFloat(winRate),
                    balance: cumulativePnl
                });
            });

            // Update win rate chart
            winRateChart.data.labels = trendData.map(d => d.date);
            winRateChart.data.datasets[0].data = trendData.map(d => d.winRate);
            winRateChart.update('none');

            // Update P&L chart
            pnlChart.data.labels = trendData.map(d => d.date);
            pnlChart.data.datasets[0].data = trendData.map(d => d.balance);
            pnlChart.update('none');
        }

        async function recordOutcome(signalId, outcome) {
            try {
                const response = await fetch('/api/record', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        signal_id: signalId,
                        outcome: outcome
                    })
                });

                if (response.ok) {
                    await fetchData();
                } else {
                    alert('Failed to record outcome');
                }
            } catch (error) {
                console.error('Error recording outcome:', error);
                alert('Error recording outcome');
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            fetchData();

            // Auto-refresh every 60 seconds
            setInterval(fetchData, 60000);
        });

        // Clear browser storage
        localStorage.clear();
        sessionStorage.clear();
    </script>
</body>
</html>
DASHBOARD_EOF

echo "🚀 Starting enhanced dashboard service..."
sudo systemctl start fxbot-dashboard.service

echo "⏱️  Waiting for service to start..."
sleep 3

echo "📊 Dashboard service status:"
systemctl status fxbot-dashboard.service --no-pager

echo ""
echo "✅ $10 TRADE TEMPLATE DASHBOARD DEPLOYED!"
echo "========================================"
echo "💰 Fixed $10 risk per trade"
echo "📊 Real dollar P&L tracking"
echo "📈 Win rate and balance charts"
echo "🎯 Enhanced bot integration ready"
echo ""
echo "📋 P&L Examples:"
echo "• Win 2:1 = +$20"
echo "• Win 3:1 = +$30"
echo "• Win 4:1 = +$40"
echo "• Loss = -$10"
echo ""
echo "🌐 Access via SSH tunnel: http://localhost:8080"
EOF

echo ""
echo "🎉 $10 TRADE TEMPLATE DASHBOARD READY!"
echo "====================================="
echo "💰 Fixed $10 risk per trade implemented"
echo "📊 Real dollar tracking with R:R calculations"
echo "🔄 Auto-refresh and chart updates enabled"
echo "✅ Ready for enhanced bot integration"