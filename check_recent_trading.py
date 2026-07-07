import pandas as pd
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = {
    "FTMO (1513511198)": r"C:\Users\bratu\Desktop\ReportHistory-1513511198.xlsx",
    "Pepperstone (62123205)": r"C:\Users\bratu\Desktop\ReportHistory-62123205.xlsx"
}

for name, file in files.items():
    print(f"\n==========================================")
    print(f"Report: {name}")
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
            
            # Use the first column as Time
            time_col_name = df.columns[0]
            trades_df[time_col_name] = pd.to_datetime(trades_df[time_col_name], errors='coerce')
            trades_df = trades_df.dropna(subset=[time_col_name])
            
            # Filter trades on June 1st and 2nd, 2026
            recent_trades = trades_df[trades_df[time_col_name] >= '2026-06-01'].copy()
            print(f"Total trades since 2026-06-01: {len(recent_trades)}")
            
            if len(recent_trades) > 0:
                print("Breakdown by symbol since 2026-06-01:")
                print(recent_trades.groupby(symbol_col_name).size())
                
                # Check when each symbol was last traded
                print("\nLast trade time for each symbol since 2026-06-01:")
                for sym, group in recent_trades.groupby(symbol_col_name):
                    print(f"  {sym}: {group[time_col_name].max()}")
            else:
                print("No recent trades since 2026-06-01.")
        else:
            print("Could not find table start.")
    except Exception as e:
        print(f"Error: {e}")
