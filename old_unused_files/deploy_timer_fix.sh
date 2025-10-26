#!/bin/bash

# This script updates the systemd timer from 5min to 30min frequency
# Run this on your Oracle server to reduce API usage by 83%

echo "🛑 Stopping current services..."
sudo systemctl stop fxbot-enhanced-watchdog.timer || true
sudo systemctl stop fxbot-enhanced-watchdog.service || true

echo "🔧 Updating timer configuration..."
sudo tee /etc/systemd/system/fxbot-enhanced-watchdog.timer > /dev/null <<TIMER_EOF
[Unit]
Description=Run ZoneSync Enhanced Watchdog every 30 minutes (API Credit Optimized)
Requires=fxbot-enhanced-watchdog.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
TIMER_EOF

echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo "▶️  Starting optimized services..."
sudo systemctl enable fxbot-enhanced-watchdog.timer
sudo systemctl start fxbot-enhanced-watchdog.timer
sudo systemctl restart fxbot-run.timer

echo "✅ Timer frequency updated: 5min → 30min (83% API reduction)"
echo "📊 Expected daily API calls: 5,760 → 960 (83% reduction)"

# Verify
systemctl status fxbot-enhanced-watchdog.timer --no-pager || true
