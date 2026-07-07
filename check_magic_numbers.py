import pandas as pd
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = {
    "FTMO": r"C:\Users\bratu\Desktop\ReportHistory-1513511198.xlsx",
    "Pepperstone": r"C:\Users\bratu\Desktop\ReportHistory-62123205.xlsx"
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
            
            # Check comment column (usually index 13)
            comment_col_idx = 13
            comment_col_name = df.columns[comment_col_idx]
            
            xau_trades = trades_df[trades_df[symbol_col_name].str.upper() == 'XAUUSD'].copy()
            xau_trades = xau_trades.dropna(subset=[comment_col_name])
            
            print(f"Unique XAUUSD comments on this account:")
            comments = xau_trades[comment_col_name].unique()
            for c in comments[:15]:
                print(f"  - {c}")
        else:
            print("Could not find table start.")
    except Exception as e:
         print(f"Error: {e}")
