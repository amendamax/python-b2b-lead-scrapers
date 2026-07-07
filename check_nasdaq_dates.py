import pandas as pd
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

file = r"C:\Users\bratu\Desktop\ReportHistory-1513511198.xlsx"
print(f"File: {file}")

try:
    df = pd.read_excel(file)
    symbol_col_idx = None
    start_row_idx = None
    for r_idx in range(len(df)):
        row_list = df.iloc[r_idx].tolist()
        if any("Symbol" in str(s) or "Simbol" in str(s) for s in row_list):
            start_row_idx = r_idx
            for c_idx, val in enumerate(row_list):
                if "Symbol" in str(val) or "Simbol" in str(val):
                    symbol_col_idx = c_idx
            break
    
    if start_row_idx is not None and symbol_col_idx is not None:
        trades_df = df.iloc[start_row_idx+1:].copy()
        symbol_col_name = df.columns[symbol_col_idx]
        trades_df[symbol_col_name] = trades_df[symbol_col_name].astype(str).str.strip()
        
        # Filter US100.cash trades
        nasdaq_trades = trades_df[trades_df[symbol_col_name] == "US100.cash"].copy()
        
        # Let's get the time column (it's the first column, index 0)
        time_col_name = df.columns[0]
        nasdaq_trades[time_col_name] = pd.to_datetime(nasdaq_trades[time_col_name])
        
        print(f"Total US100.cash trades: {len(nasdaq_trades)}")
        if len(nasdaq_trades) > 0:
            print("First trade time:", nasdaq_trades[time_col_name].min())
            print("Last trade time:", nasdaq_trades[time_col_name].max())
            print("\nRecent NASDAQ trades (last 10 rows of NASDAQ):")
            print(nasdaq_trades.tail(10).to_string())
        else:
            print("No US100.cash trades found.")
    else:
        print("Could not find table start.")
except Exception as e:
    print(f"Error: {e}")
