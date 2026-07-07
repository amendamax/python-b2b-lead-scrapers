import MetaTrader5 as mt5
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

terminals = {
    "FTMO": r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe",
    "Pepperstone": r"C:\Program Files\Pepperstone MetaTrader 5\terminal64.exe"
}

print(f"Current local time: {datetime.now()}")

for name, path in terminals.items():
    print(f"\n==========================================")
    print(f"Terminal: {name}")
    if not mt5.initialize(path=path):
        print(f"Error initializing: {mt5.last_error()}")
        continue
    try:
        symbol = "XAUUSD"
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print("Failed to get tick.")
            continue
            
        print(f"Tick time (epoch): {tick.time}")
        print(f"Tick time (local-converted): {datetime.fromtimestamp(tick.time)}")
        
        # Get terminal time details
        terminal_info = mt5.terminal_info()
        print(f"Terminal name: {terminal_info.name if terminal_info else 'Unknown'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mt5.shutdown()
