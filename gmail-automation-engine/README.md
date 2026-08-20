# 🚀 Gmail Multi-Account Automation Engine — Milestone 1

Production-grade, crash-resilient multi-account automation and dispatcher engine built with Python, SQLite WAL mode, and Playwright session architecture.

---

## 📁 File Structure & Schema

| File | Type | Description |
| :--- | :--- | :--- |
| **`config.txt`** | Text (Key=Value) | Global runtime parameters (workers, delays, limits, TLS, timeouts). |
| **`app_passwords.json`** | JSON | The **ONLY** JSON data file: Maps Gmail accounts to 16-char app passwords. |
| **`accounts.txt`** | Text (1 per line) | List of active sender Gmail accounts. |
| **`leads.txt`** | Text (1 per line) | Target recipient email queue with automated deduplication. |
| **`letter.html`** | HTML Template | Email body template with dynamic placeholder injection (`{{recipient_name}}`, `{{tracking_link}}`, `{{message_ref}}`). |
| **`links.txt`** | Text (1 per line) | Pool of rotation URLs injected into letter templates. |
| **`24-reached.txt`** | Append Log | Automatically logs accounts reaching daily quota with cooldown timestamp. |

---

## ⚙️ Core Architecture Modules

- **`file_parser.py`**: Robust, typed parsers for all 7 user-facing files with validation.
- **`database.py`**: SQLite database with Write-Ahead Logging (WAL), busy timeout handling, and atomic queue row-locking (`pending` -> `in_flight` -> `completed`).
- **`account_manager.py`**: State machine managing account rotation, daily quotas, and automated cooldown transitions.
- **`test_milestone1.py`**: Standalone test harness verifying 100% of Milestone 1 deliverables.

---

## 🧪 Verification Execution

To run the complete Milestone 1 test harness:
```bash
python test_milestone1.py
```
