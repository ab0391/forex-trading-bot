#!/bin/bash
# Switch Dashboard to Port 80 (bypasses Oracle Cloud firewall issues)

echo "🔧 Switching Dashboard to Port 80"
echo "================================="

# SSH into server and make the changes
ssh fxbot << 'EOF'
cd /home/ubuntu/fxbot

echo "🛑 Stopping current dashboard service..."
sudo systemctl stop fxbot-dashboard.service

echo "📝 Updating dashboard server to use port 80..."
# Backup original
cp dashboard_server.py dashboard_server_8502_backup.py

# Update port to 80 in dashboard_server.py
sed -i 's/port=8502/port=80/g' dashboard_server.py

echo "🔧 Updating systemd service..."
sudo tee /etc/systemd/system/fxbot-dashboard.service > /dev/null <<SERVICE_EOF
[Unit]
Description=ZoneSync Trading Dashboard
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/ubuntu/fxbot
Environment=PYTHONPATH=/home/ubuntu/fxbot
ExecStart=/home/ubuntu/fxbot/.venv/bin/python3 dashboard_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "🔄 Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable fxbot-dashboard.service
sudo systemctl start fxbot-dashboard.service

echo "⏱️  Waiting for service to start..."
sleep 3

echo "🧪 Testing local access..."
curl -I http://localhost:80

echo "📊 Service status:"
systemctl status fxbot-dashboard.service --no-pager

echo ""
echo "✅ Dashboard moved to port 80!"
echo "🌐 Access at: http://84.235.245.60"
echo "📝 Original backed up as: dashboard_server_8502_backup.py"
EOF

echo ""
echo "🎉 DASHBOARD NOW ON PORT 80!"
echo "============================"
echo "🌐 New URL: http://84.235.245.60"
echo "✅ No port number needed"
echo "✅ Should work immediately (port 80 is always open)"