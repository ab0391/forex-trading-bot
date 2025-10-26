#!/bin/bash
# Deploy Improved Dashboard with P&L Percentage and Bug Fixes

echo "🔧 Deploying Improved Dashboard"
echo "==============================="

# Upload improved dashboard server
scp dashboard_server.py fxbot:/home/ubuntu/fxbot/

# SSH and create improved dashboard HTML
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot

echo "🔨 Creating improved dashboard HTML with bug fixes..."

cat > trading_dashboard.html << 'DASHBOARD_EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZoneSync Trading Dashboard</title>
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
            overflow-x: hidden; /* Prevent horizontal scroll */
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            min-height: calc(100vh - 40px); /* Fixed height calculation */
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
            min-height: 120px; /* Fixed height */
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
            height: 350px; /* Fixed height */
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
            min-height: 250px; /* Minimum chart height */
        }

        .signals-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(255, 255, 255, 0.1);
            max-height: 500px; /* Prevent infinite growth */
            overflow-y: auto; /* Scroll if too many signals */
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
            min-height: 70px; /* Fixed minimum height */
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
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

        /* Scrollbar styling */
        .signals-section::-webkit-scrollbar {
            width: 8px;
        }

        .signals-section::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        .signals-section::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 4px;
        }

        .signals-section::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 ZoneSync Trading Dashboard</h1>
            <p>Real-Time Performance Tracking with Enhanced Price Accuracy</p>
            <p><strong>Fresh Start:</strong> Accurate tracking with R-based P&L</p>
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
                <div class="stat-value" id="netPnl">+0%</div>
                <div class="stat-label">Net P&L (%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="currentStreak">-</div>
                <div class="stat-label">Current Streak</div>
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
                <div class="chart-title">Performance by Pair</div>
                <div class="chart-wrapper">
                    <canvas id="pairChart"></canvas>
                </div>
            </div>
        </div>

        <div class="signals-section">
            <h3>Recent Signals</h3>
            <div id="signalsList">
                <div class="clean-slate">
                    <h4>🎉 Clean Slate!</h4>
                    <p>No signals yet - fresh tracking with accurate real-time prices</p>
                    <p>New signals will use R-based P&L calculation</p>
                    <p><strong>Win:</strong> +R (your risk/reward ratio) | <strong>Loss:</strong> -1R</p>
                </div>
            </div>
        </div>

        <div class="refresh-info">
            <p>📊 Dashboard auto-refreshes every 60 seconds</p>
            <p>🎯 P&L calculated as Risk/Reward percentage (R-based)</p>
            <p id="lastUpdate">Last updated: Never (Fresh start)</p>
        </div>
    </div>

    <script>
        // Global chart variables
        let winRateChart = null;
        let pairChart = null;

        function initializeCharts() {
            // Destroy existing charts if they exist
            if (winRateChart) {
                winRateChart.destroy();
            }
            if (pairChart) {
                pairChart.destroy();
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

            // Performance by Pair Chart
            const pairCtx = document.getElementById('pairChart').getContext('2d');
            pairChart = new Chart(pairCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Win Rate %',
                        data: [],
                        backgroundColor: [
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)',
                            'rgba(255, 152, 0, 0.8)',
                            'rgba(156, 39, 176, 0.8)',
                            'rgba(244, 67, 54, 0.8)'
                        ],
                        borderColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#FF9800',
                            '#9C27B0',
                            '#F44336'
                        ],
                        borderWidth: 2
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
        }

        function updateStats(stats) {
            document.getElementById('winRate').textContent = stats.win_rate + '%';
            document.getElementById('totalTrades').textContent = stats.total_trades;

            // Display P&L as percentage with proper sign
            const pnlText = stats.net_pnl_percentage >= 0 ?
                '+' + stats.net_pnl_percentage + '%' :
                stats.net_pnl_percentage + '%';
            document.getElementById('netPnl').textContent = pnlText;

            // Color code the P&L
            const pnlElement = document.getElementById('netPnl');
            if (stats.net_pnl_percentage > 0) {
                pnlElement.style.color = '#4CAF50';
            } else if (stats.net_pnl_percentage < 0) {
                pnlElement.style.color = '#f44336';
            } else {
                pnlElement.style.color = '#ffffff';
            }

            if (stats.current_streak > 0) {
                const streakType = stats.streak_type === 'win' ? 'W' : 'L';
                const streakColor = stats.streak_type === 'win' ? '#4CAF50' : '#f44336';
                const streakElement = document.getElementById('currentStreak');
                streakElement.textContent = streakType + stats.current_streak;
                streakElement.style.color = streakColor;
            } else {
                document.getElementById('currentStreak').textContent = '-';
                document.getElementById('currentStreak').style.color = '#ffffff';
            }
        }

        function updateSignals(signals) {
            const signalsList = document.getElementById('signalsList');

            if (signals.length === 0) {
                signalsList.innerHTML = `
                    <div class="clean-slate">
                        <h4>🎉 Clean Slate!</h4>
                        <p>No signals yet - fresh tracking with accurate real-time prices</p>
                        <p>New signals will use R-based P&L calculation</p>
                        <p><strong>Win:</strong> +R (your risk/reward ratio) | <strong>Loss:</strong> -1R</p>
                    </div>
                `;
                return;
            }

            // Show recent signals (last 15)
            const recentSignals = signals.slice(-15).reverse();
            signalsList.innerHTML = recentSignals.map(signal => {
                const statusClass = signal.outcome ? '' : 'signal-pending';
                const outcomeButtons = signal.outcome ?
                    `<span style="color: ${signal.outcome === 'win' ? '#4CAF50' : '#f44336'}; font-weight: bold;">
                        ${signal.outcome === 'win' ? '✅' : '❌'} ${signal.outcome.toUpperCase()}
                        ${signal.outcome === 'win' ? ' (+' + (signal.risk_reward || 2) + 'R)' : ' (-1R)'}
                    </span>` :
                    `<div class="signal-buttons">
                        <button class="btn btn-win" onclick="recordOutcome('${signal.signal_id}', 'win')">✅ Win</button>
                        <button class="btn btn-loss" onclick="recordOutcome('${signal.signal_id}', 'loss')">❌ Loss</button>
                    </div>`;

                return `
                    <div class="signal-item ${statusClass}">
                        <div class="signal-info">
                            <strong>${signal.symbol}</strong> ${signal.zone_type.toUpperCase()}
                            <div class="signal-details">Entry: ${signal.entry} | R:R: ${signal.risk_reward}</div>
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

            completedTrades.forEach((signal, index) => {
                if (signal.outcome === 'win') wins++;
                const winRate = ((wins / (index + 1)) * 100).toFixed(1);
                trendData.push({
                    x: new Date(signal.outcome_timestamp || signal.timestamp).toLocaleDateString(),
                    y: parseFloat(winRate)
                });
            });

            winRateChart.data.labels = trendData.map(d => d.x);
            winRateChart.data.datasets[0].data = trendData.map(d => d.y);
            winRateChart.update('none');

            // Performance by pair
            const pairStats = {};
            completedTrades.forEach(signal => {
                if (!pairStats[signal.symbol]) {
                    pairStats[signal.symbol] = { wins: 0, total: 0 };
                }
                pairStats[signal.symbol].total++;
                if (signal.outcome === 'win') {
                    pairStats[signal.symbol].wins++;
                }
            });

            const pairLabels = Object.keys(pairStats);
            const pairWinRates = pairLabels.map(pair =>
                (pairStats[pair].wins / pairStats[pair].total * 100).toFixed(1)
            );

            pairChart.data.labels = pairLabels;
            pairChart.data.datasets[0].data = pairWinRates;
            pairChart.update('none');
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

echo "✅ Improved dashboard HTML created"

# Restart services
echo "🔄 Restarting dashboard service..."
sudo systemctl restart fxbot-dashboard.service
sleep 3

if systemctl is-active --quiet fxbot-dashboard.service; then
    echo "✅ Dashboard service restarted successfully"
else
    echo "❌ Dashboard restart failed"
    journalctl -u fxbot-dashboard.service -n 10 --no-pager
fi

echo ""
echo "🎉 IMPROVED DASHBOARD DEPLOYED!"
echo "=============================="
echo "✅ P&L now shows as percentage (R-based)"
echo "✅ Fixed UI bugs and screen extension issues"
echo "✅ Improved mobile responsiveness"
echo "✅ Better chart sizing and layout"
echo "✅ Enhanced visual design"

echo ""
echo "📊 New P&L Calculation:"
echo "• Win: +R (your actual risk/reward ratio)"
echo "• Loss: -1R (always -100% of risk)"
echo "• Example: 2 wins at 2R + 1 loss = +3R total = +100% net P&L"

echo ""
echo "🔧 UI Fixes Applied:"
echo "• Fixed container height calculations"
echo "• Prevented horizontal scroll"
echo "• Fixed chart sizing issues"
echo "• Improved signal list scrolling"
echo "• Better mobile layout"
echo "• Enhanced button interactions"

echo ""
echo "$(date): Improved dashboard deployment completed"
EOF

echo ""
echo "🚀 IMPROVED DASHBOARD DEPLOYED!"
echo "==============================="
echo "📊 P&L now calculated as Risk/Reward percentage"
echo "🔧 UI bugs fixed - no more screen extension"
echo "📱 Better mobile responsiveness"
echo ""
echo "🎯 Refresh your dashboard: http://localhost:8502"