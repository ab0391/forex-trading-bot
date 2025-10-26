# ZoneSync Stability Deployment - Quick Guide

## Step 1: Upload Files to Oracle Server

Upload these files to `/home/ubuntu/fxbot/` on your Oracle server:

### Required Files:
- ✅ `multi_strategy_trading_tool_fixed.py`
- ✅ `robust_notifier.py`
- ✅ `zones_block_fixed.py`
- ✅ `enhanced_network_watchdog.py`
- ✅ `enhanced_h4_bias.py`
- ✅ `deploy_stability_fixes.sh`

### Upload Methods:
**Option A: SCP (if you have SSH access)**
```bash
scp multi_strategy_trading_tool_fixed.py ubuntu@your-oracle-ip:/home/ubuntu/fxbot/
scp robust_notifier.py ubuntu@your-oracle-ip:/home/ubuntu/fxbot/
scp zones_block_fixed.py ubuntu@your-oracle-ip:/home/ubuntu/fxbot/
scp enhanced_network_watchdog.py ubuntu@your-oracle-ip:/home/ubuntu/fxbot/
scp enhanced_h4_bias.py ubuntu@your-oracle-ip:/home/ubuntu/fxbot/
scp deploy_stability_fixes.sh ubuntu@your-oracle-ip:/home/ubuntu/fxbot/
```

**Option B: Oracle Cloud Console (Upload via web interface)**
- Use Oracle Cloud Console file manager
- Navigate to `/home/ubuntu/fxbot/`
- Upload each file individually

## Step 2: Run Deployment Script

SSH into your Oracle server and run:

```bash
cd /home/ubuntu/fxbot
chmod +x deploy_stability_fixes.sh
./deploy_stability_fixes.sh
```

## Step 3: Monitor Deployment

The script will:
- ✅ Create automatic backup
- ✅ Install dependencies
- ✅ Deploy stability fixes
- ✅ Update systemd services
- ✅ Start enhanced monitoring
- ✅ Test notifications
- ✅ Generate health report

## Step 4: Verification

After deployment, verify everything is working:

```bash
# Check service status
systemctl status fxbot-run.timer fxbot-enhanced-watchdog.timer

# Monitor live logs
journalctl -u fxbot-run.service -f

# Generate health report
cd /home/ubuntu/fxbot
.venv/bin/python3 enhanced_network_watchdog.py --report

# Test notifications
.venv/bin/python3 -c "from robust_notifier import notifier; print(notifier.test_notifications())"
```

## Expected Results

After successful deployment:
- ✅ **No more server reboots needed**
- ✅ **Robust error handling** - Bot recovers from failures automatically
- ✅ **Connection pooling** - Faster, more reliable API calls
- ✅ **SMTP timeouts fixed** - Email notifications won't hang
- ✅ **Enhanced monitoring** - System self-heals from problems
- ✅ **Missing function restored** - No more NameError crashes

## Next Phase: H4 Bias Enhancement

Once stability is confirmed (24-48 hours), we'll integrate the H4 bias system to improve your win rate from 33% to 50%+.

## Rollback Plan

If anything goes wrong:
```bash
cd /home/ubuntu/fxbot

# Stop new services
sudo systemctl stop fxbot-enhanced-watchdog.timer
sudo systemctl disable fxbot-enhanced-watchdog.timer

# Restore original files
cp multi_strategy_trading_tool_original.py multi_strategy_trading_tool.py
cp notifier_original.py notifier.py
cp zones_block_original.py zones_block.py

# Restart original services
sudo systemctl restart fxbot-run.service
```

## Support

If you encounter issues:
1. Check logs: `journalctl -u fxbot-run.service -n 50`
2. Check health: `.venv/bin/python3 enhanced_network_watchdog.py --report`
3. Verify files uploaded correctly: `ls -la /home/ubuntu/fxbot/`

**Ready to deploy? Upload the files and run the script!**