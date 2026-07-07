import MetaTrader5 as mt5
import sys

# Reconfigure stdout to handle encoding errors on Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

terminals = {
    "FTMO": r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe",
    "Pepperstone": r"C:\Program Files\Pepperstone MetaTrader 5\terminal64.exe"
}

for name, path in terminals.items():
    print(f"\n==========================================")
    print(f"Terminal: {name} ({path})")
    
    if not mt5.initialize(path=path):
        print(f"Error initializing MT5 for {name}: {mt5.last_error()}")
        continue
        
    try:
        # Check connection status
        terminal_info = mt5.terminal_info()
        acc_info = mt5.account_info()
        if terminal_info:
            print(f"Connected: {terminal_info.connected}")
        if acc_info:
            print(f"Account: {acc_info.login} (Company: {acc_info.company})")
            
        # Get all symbols
        symbols = mt5.symbols_get()
        print(f"Total symbols available: {len(symbols)}")
        
        # Look for NASDAQ, SP500, Gold and similar symbols
        search_terms = ["US100", "US500", "USTEC", "SPX", "XAU", "GOLD", "EURUSD", "BTC"]
        found_symbols = []
        for sym in symbols:
            name_upper = sym.name.upper()
            if any(term in name_upper for term in search_terms):
                found_symbols.append(sym.name)
                
        print(f"Matching symbols: {sorted(found_symbols[:50])}")
        
    except Exception as e:
        print(f"Error checking {name}: {e}")
    finally:
        mt5.shutdown()
