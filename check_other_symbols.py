import pandas as pd
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

file = r"C:\Users\bratu\Desktop\ReportHistory-62123205.xlsx"
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
        
        # Check comments column (which is the last column, usually index 13)
        comment_col_idx = 13
        comment_col_name = df.columns[comment_col_idx]
        
        for sym in ["BTCUSD", "SpotCrude"]:
            sym_trades = trades_df[trades_df[symbol_col_name] == sym]
            print(f"\nSymbol: {sym} (Total trades: {len(sym_trades)})")
            if len(sym_trades) > 0:
                print("Sample comments:")
                print(sym_trades[comment_col_name].dropna().unique()[:10])
                print("First 3 trades:")
                print(sym_trades.head(3).to_string())
                print("Last 3 trades:")
                print(sym_trades.tail(3).to_string())
            else:
                print("No trades found.")
    else:
        print("Table start not found.")
except Exception as e:
    print(f"Error: {e}")
