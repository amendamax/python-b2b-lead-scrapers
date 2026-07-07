import MetaTrader5 as mt5
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

terminals = {
    "FTMO": r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe",
    "Pepperstone": r"C:\Program Files\Pepperstone MetaTrader 5\terminal64.exe"
}

for name, path in terminals.items():
    print(f"\n==========================================")
    print(f"Terminal: {name}")
    
    if not mt5.initialize(path=path):
        print(f"Error initializing: {mt5.last_error()}")
        continue
        
    try:
        symbol = "XAUUSD"
        tf = mt5.TIMEFRAME_M5
        
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, 300)
        if rates is None:
            print(f"[X] copy_rates_from_pos returned None! Error code: {mt5.last_error()}")
        else:
            print(f"[OK] Successfully downloaded {len(rates)} rates.")
            if len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                print(f"  First bar time: {df['time'].min()}")
                print(f"  Last bar time: {df['time'].max()}")
                print(f"  First close: {df['close'].iloc[0]} | Last close: {df['close'].iloc[-1]}")
            else:
                print("  Returned 0 rates.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mt5.shutdown()
