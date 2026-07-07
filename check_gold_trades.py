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
        # Find where trade records start
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
            # Clean up empty rows
            trades_df = trades_df.dropna(subset=[df.columns[symbol_col_idx]])
            
            # Filter XAUUSD trades
            # Check the actual values in symbol column to handle potential spaces/case
            symbol_col_name = df.columns[symbol_col_idx]
            trades_df[symbol_col_name] = trades_df[symbol_col_name].astype(str).str.strip()
            
            xau_trades = trades_df[trades_df[symbol_col_name].str.upper() == 'XAUUSD']
            print(f"Total XAUUSD trades: {len(xau_trades)}")
            if len(xau_trades) > 0:
                print("First 3 XAUUSD trades:")
                print(xau_trades.head(3).to_string())
                print("Last 3 XAUUSD trades:")
                print(xau_trades.tail(3).to_string())
            else:
                print("NO XAUUSD trades found in this report.")
        else:
            print("Could not find Trade/Symbol table start.")
    except Exception as e:
        print(f"Error: {e}")
