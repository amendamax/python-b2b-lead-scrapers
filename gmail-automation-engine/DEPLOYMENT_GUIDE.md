# 🚀 Production Deployment & Operations Guide

## 1. Quick Start (Standalone Execution)
To run the dispatcher manually in console:
```bash
python3 bulk.py
```

---

## 2. Overnight Unattended Daemon Execution (Linux / systemd)
To run as a 24/7 background service with auto-restart on system reboot or crash:
```bash
# 1. Run the one-click installer
chmod +x deploy_server.sh
./deploy_server.sh

# 2. Start the daemon
systemctl start gmail-mailer

# 3. Check live status
systemctl status gmail-mailer

# 4. View real-time streaming logs
tail -f logs/engine.log
```

---

## 3. Crash & Zero-Duplicate Recovery Behavior
- **Atomic Transactions**: Leads transition deterministically (`pending` -> `in_flight` -> `completed`).
- **Crash Sweep**: If the machine reboots or the process terminates abruptly, on next launch the engine automatically checks Gmail `Sent Mail` via IMAP for in-flight `Message-ID` headers.
- **Guarantee**: Confirmed sent emails are marked `completed`; unconfirmed emails are quarantined/reset without any double-sending.

---

## 4. Quota & 24h Cooldown Logging
When an account exhausts its daily sending quota (`DEFAULT_DAILY_LIMIT_PER_ACCOUNT` in `config.txt`):
- It is placed into cooldown until midnight UTC.
- The event is appended to `24-reached.txt`.
- The engine seamlessly rotates to the next available account in the pool.
