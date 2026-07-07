import MetaTrader5 as mt5
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
        sym_info = mt5.symbol_info(symbol)
        if sym_info is None:
            print(f"Symbol {symbol} not found.")
            continue
            
        filling_mode = sym_info.filling_mode
        print(f"Symbol: {symbol}")
        print(f"  Raw filling_mode: {filling_mode}")
        
        # Check flags
        # SYMBOL_FILLING_FOK = 1
        # SYMBOL_FILLING_IOC = 2
        fok_supported = bool(filling_mode & 1)
        ioc_supported = bool(filling_mode & 2)
        
        print(f"  FOK (Fill or Kill) supported: {fok_supported}")
        print(f"  IOC (Immediate or Cancel) supported: {ioc_supported}")
        
        # Determine what each bot's get_filling_type would return:
        # AUR_FTMO code:
        ftmo_fill = "IOC" if (filling_mode & 2) else ("FOK" if (filling_mode & 1) else "RETURN")
        # XAUUSD code:
        pep_fill = "FOK" if (filling_mode & 1) else ("IOC" if (filling_mode & 2) else "RETURN")
        
        print(f"  AUR_FTMO get_filling_type() would return: {ftmo_fill}")
        print(f"  XAUUSD get_filling_type() would return: {pep_fill}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mt5.shutdown()
