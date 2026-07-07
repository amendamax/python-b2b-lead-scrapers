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
        acc_info = mt5.account_info()
        if acc_info is None:
            print("Failed to get account info.")
            continue
            
        print(f"Account Login: {acc_info.login}")
        print(f"Balance: {acc_info.balance} {acc_info.currency}")
        print(f"Equity: {acc_info.equity}")
        print(f"Margin Free: {acc_info.margin_free}")
        print(f"Leverage: 1:{acc_info.leverage}")
        
        symbol = "XAUUSD"
        sym_info = mt5.symbol_info(symbol)
        if sym_info is None:
            print(f"Symbol {symbol} info not found.")
            continue
            
        print(f"Symbol: {symbol}")
        print(f"  Spread: {sym_info.spread} points")
        print(f"  Contract size: {sym_info.trade_contract_size}")
        print(f"  Min Volume: {sym_info.volume_min}")
        print(f"  Max Volume: {sym_info.volume_max}")
        print(f"  Volume Step: {sym_info.volume_step}")
        print(f"  Trade Mode: {sym_info.trade_mode}")
        print(f"  Execution Mode: {sym_info.execution_mode}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mt5.shutdown()
