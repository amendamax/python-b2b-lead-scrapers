#!/bin/bash
# ==============================================================================
# GMAIL AUTOMATION ENGINE - 1-CLICK PRODUCTION SERVER INSTALLER
# ==============================================================================

set -e

echo ">>> [1/4] Updating system packages..."
apt-get update -y && apt-get install -y python3 python3-pip sqlite3 git curl

echo ">>> [2/4] Installing Python dependencies..."
pip3 install playwright || true
playwright install-deps || true
playwright install chromium || true

echo ">>> [3/4] Setting up directory permissions & logs..."
mkdir -p /root/gmail-automation-engine/logs
mkdir -p /root/gmail-automation-engine/data
chmod +x /root/gmail-automation-engine/bulk.py

echo ">>> [4/4] Configuring systemd background daemon..."
cp /root/gmail-automation-engine/gmail-mailer.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable gmail-mailer.service

echo "================================================================================"
echo "   DEPLOYMENT COMPLETE! RUN COMMANDS:"
echo "   Start Engine:   systemctl start gmail-mailer"
echo "   Status:         systemctl status gmail-mailer"
echo "   View Live Logs: tail -f /root/gmail-automation-engine/logs/engine.log"
echo "   Run Manually:   python3 bulk.py"
echo "================================================================================"
