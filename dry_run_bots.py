import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import xgboost as xgb
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def get_mt5_timeframe(tf_str):
    mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }
    return mapping.get(tf_str.upper(), mt5.TIMEFRAME_M5)

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calculate_atr(df, window=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=window).mean()

def dry_run_bot(name, path, folder):
    print(f"\n==========================================")
    print(f"DRY RUN: {name}")
    print(f"Directory: {folder}")
    
    # Load configuration
    try:
        with open(f"{folder}/config.json", "r") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"  Error loading config: {e}")
        return
        
    mt5_path = cfg.get("mt5_path")
    if not mt5.initialize(path=mt5_path):
        print(f"  Error initializing MT5: {mt5.last_error()}")
        return
        
    try:
        # Load model
        model = xgb.XGBClassifier()
        model.load_model(f"{folder}/model.json")
        
        SYMBOL = cfg.get("symbol", "XAUUSD")
        TF_STR = cfg.get("timeframe", "M5")
        TF = get_mt5_timeframe(TF_STR)
        THRESHOLD = cfg.get("prob_threshold", 0.58)
        
        # Download rates
        rates = mt5.copy_rates_from_pos(SYMBOL, TF, 0, 300)
        if rates is None or len(rates) < 200:
            print("  Error copying rates from MT5.")
            return
            
        df_live = pd.DataFrame(rates)
        df_live['mid'] = (df_live['close'] + df_live['open']) / 2.0
        
        # Volatility and Volume
        df_live['spread_feat'] = df_live['spread']
        df_live['volume_feat'] = np.log1p(df_live['tick_volume'])
        df_live['atr'] = calculate_atr(df_live, window=14)
        df_live['volatility_20'] = df_live['mid'].pct_change().rolling(window=20).std()
        
        # RSI
        df_live['rsi'] = calculate_rsi(df_live['mid'], window=14)
        
        # SMA distances
        df_live['sma_20'] = df_live['mid'].rolling(window=20).mean()
        df_live['sma_50'] = df_live['mid'].rolling(window=50).mean()
        df_live['sma_200'] = df_live['mid'].rolling(window=200).mean()
        df_live['sma_20_dist'] = (df_live['mid'] - df_live['sma_20']) / (df_live['sma_20'] + 1e-9)
        df_live['sma_50_dist'] = (df_live['mid'] - df_live['sma_50']) / (df_live['sma_50'] + 1e-9)
        df_live['sma_200_dist'] = (df_live['mid'] - df_live['sma_200']) / (df_live['sma_200'] + 1e-9)
        
        # ROC
        df_live['roc_10'] = (df_live['mid'] - df_live['mid'].shift(10)) / (df_live['mid'].shift(10) + 1e-9)
        df_live['roc_30'] = (df_live['mid'] - df_live['mid'].shift(30)) / (df_live['mid'].shift(30) + 1e-9)
        
        # Time features
        df_live['time'] = pd.to_datetime(df_live['time'], unit='s')
        df_live['hour'] = df_live['time'].dt.hour
        df_live['is_asian_session'] = ((df_live['hour'] >= 23) | (df_live['hour'] < 8)).astype(int)
        df_live['is_london_session'] = ((df_live['hour'] >= 8) & (df_live['hour'] < 14)).astype(int)
        df_live['is_ny_session'] = ((df_live['hour'] >= 14) & (df_live['hour'] < 22)).astype(int)
        
        latest = df_live.iloc[-1]
        
        print(f"  Last Candle Time (Server): {latest['time']}")
        print(f"  Hour feature value: {latest['hour']}")
        print(f"  Sessions: Asian={latest['is_asian_session']} | London={latest['is_london_session']} | NY={latest['is_ny_session']}")
        print(f"  RSI: {latest['rsi']:.2f} | ATR: {latest['atr']:.4f} | Spread: {latest['spread_feat']}")
        
        # Features cols
        features_cols = [
            "spread_feat", "volume_feat", "atr", "volatility_20", "rsi",
            "sma_20_dist", "sma_50_dist", "sma_200_dist", "roc_10", "roc_30",
            "is_asian_session", "is_london_session", "is_ny_session"
        ]
        
        input_data = pd.DataFrame([latest[features_cols].values], columns=features_cols)
        print("  Input features:")
        for col in features_cols:
            print(f"    {col}: {latest[col]}")
            
        # Predict
        probabilities = model.predict_proba(input_data)[0]
        prob_buy = probabilities[1]
        prob_sell = probabilities[2]
        
        print(f"\n  Model Output Probabilities:")
        print(f"    Class 0 (Hold/None): {probabilities[0]:.4f}")
        print(f"    Class 1 (BUY):       {prob_buy:.4f}")
        print(f"    Class 2 (SELL):      {prob_sell:.4f}")
        print(f"    Threshold set:       {THRESHOLD:.2f}")
        
        if prob_buy >= THRESHOLD:
            print("  ==> DECISION: TRIGGER BUY")
        elif prob_sell >= THRESHOLD:
            print("  ==> DECISION: TRIGGER SELL")
        else:
            print("  ==> DECISION: NO TRADE (probabilities below threshold)")
            
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        mt5.shutdown()

dry_run_bot("FTMO Gold Bot", r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe", r"C:\Users\bratu\Desktop\New folder\AUR_FTMO")
dry_run_bot("Pepperstone Gold Bot", r"C:\Program Files\Pepperstone MetaTrader 5\terminal64.exe", r"C:\Users\bratu\Desktop\New folder\XAUUSD")
