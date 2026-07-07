import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

folders = {
    "FTMO Gold Bot": r"C:\Users\bratu\Desktop\New folder\AUR_FTMO\bot_trading_gold_ftmo.log",
    "Pepperstone Gold Bot": r"C:\Users\bratu\Desktop\New folder\XAUUSD\bot_trading_gold.log"
}

for name, filepath in folders.items():
    print(f"\n==========================================")
    print(f"Bot: {name} ({filepath})")
    if not os.path.exists(filepath):
        print("Log file does not exist.")
        continue
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        print(f"Total lines: {len(lines)}")
        print("Last 20 lines:")
        print("".join(lines[-20:]))
    except Exception as e:
        print(f"Error: {e}")
