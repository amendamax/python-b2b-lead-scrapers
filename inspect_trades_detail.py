import pandas as pd
import numpy as np
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
            
            # Filter XAUUSD trades
            xau_trades = trades_df[trades_df[symbol_col_name].str.upper() == 'XAUUSD'].copy()
            
            # Let's parse Entry Time (column 0) and Exit Time (column 8)
            time_in_col = df.columns[0]
            time_out_col = df.columns[8]
            
            xau_trades[time_in_col] = pd.to_datetime(xau_trades[time_in_col], errors='coerce')
            xau_trades[time_out_col] = pd.to_datetime(xau_trades[time_out_col], errors='coerce')
            
            # Drop invalid/metadata rows
            xau_trades = xau_trades.dropna(subset=[time_in_col, time_out_col])
            
            # Filter since June 1st
            xau_recent = xau_trades[xau_trades[time_in_col] >= '2026-06-01'].copy()
            print(f"Total XAUUSD trades since 2026-06-01: {len(xau_recent)}")
            
            if len(xau_recent) > 0:
                # Calculate durations in seconds
                durations = (xau_recent[time_out_col] - xau_recent[time_in_col]).dt.total_seconds()
                print(f"  Average holding duration: {durations.mean():.2f} seconds ({durations.mean()/60:.2f} minutes)")
                print(f"  Min holding duration: {durations.min():.2f} seconds")
                print(f"  Max holding duration: {durations.max():.2f} seconds")
                
                # Check volumes
                volume_col = df.columns[4] # Volume
                xau_recent[volume_col] = pd.to_numeric(xau_recent[volume_col], errors='coerce')
                print(f"  Average volume (lots): {xau_recent[volume_col].mean():.2f} lots")
                print(f"  Min volume (lots): {xau_recent[volume_col].min():.2f} lots")
                print(f"  Max volume (lots): {xau_recent[volume_col].max():.2f} lots")
                
                # Profit/Loss distribution
                profit_col = df.columns[12] # Profit
                xau_recent[profit_col] = pd.to_numeric(xau_recent[profit_col], errors='coerce')
                print(f"  Total net profit/loss: {xau_recent[profit_col].sum():.2f} USD")
                print(f"  Average profit/loss: {xau_recent[profit_col].mean():.2f} USD")
                print(f"  Win rate: {len(xau_recent[xau_recent[profit_col] > 0]) / len(xau_recent) * 100:.2f}%")
            else:
                print("No recent XAUUSD trades.")
        else:
            print("Could not find table start.")
    except Exception as e:
         print(f"Error: {e}")
