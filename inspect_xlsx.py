import pandas as pd
import openpyxl
import sys

# Reconfigure stdout to handle encoding errors on Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = [
    r"C:\Users\bratu\Desktop\ReportHistory-1513511198.xlsx",
    r"C:\Users\bratu\Desktop\ReportHistory-62123205.xlsx"
]

for file in files:
    print(f"\n==========================================")
    print(f"File: {file}")
    try:
        # load workbook to see sheet names
        wb = openpyxl.load_workbook(file, read_only=True)
        print(f"Sheet names: {wb.sheetnames}")
        
        # Read with pandas
        df = pd.read_excel(file)
        print(f"Shape: {df.shape}")
        
        # Show the first few metadata rows (rows 0-5 contain Name, Account, Company, Date info)
        for i in range(min(5, len(df))):
            row_vals = df.iloc[i].dropna().tolist()
            if row_vals:
                print(f"Meta Row {i}: {row_vals}")
                
        # Find where trade records start and summarize symbols
        # Columns might not be named, let's find the symbol column
        # In the Pepperstone UK report, we see Time, Position, Symbol, Type, Volume, Price... starting around index 5
        # Let's search for "Symbol" in the dataframe to find where the table starts
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
            print(f"Trades start at row {start_row_idx}, Symbol column is index {symbol_col_idx}")
            trades_df = df.iloc[start_row_idx+1:].copy()
            # Clean up and find symbols
            symbols = trades_df.iloc[:, symbol_col_idx].dropna().unique()
            print(f"Traded symbols: {symbols}")
            # Count of trades
            print(f"Total trades/orders: {len(trades_df.dropna(subset=[df.columns[symbol_col_idx]]))}")
            
            # Let's show a few actual trades
            valid_trades = trades_df.dropna(subset=[df.columns[symbol_col_idx]]).head(10)
            print("\nFirst 10 trades:")
            print(valid_trades.to_string())
        else:
            print("Could not find Trade/Symbol table start.")
            print(df.head(15).to_string())
            
    except Exception as e:
        import traceback
        print(f"Error reading file: {e}")
        traceback.print_exc()

