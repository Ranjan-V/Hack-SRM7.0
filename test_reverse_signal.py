import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backtest.engine import OFIBacktester
import pandas as pd

# Load test data
df = pd.read_csv('data/processed/features_engineered.csv')
split_idx = int(len(df) * 0.8)
df_test = df.iloc[split_idx:].reset_index(drop=True)

# REVERSE THE SIGNAL
df_test['ofi_mean_50_reversed'] = -df_test['ofi_mean_50']

print("\n" + "="*70)
print("TESTING REVERSED OFI SIGNAL")
print("="*70)
print("Strategy: SELL when OFI high, BUY when OFI low")
print("(Fading the signal during downtrend)")
print("="*70 + "\n")

backtester = OFIBacktester(df_test, initial_capital=10000)

metrics = backtester.run_strategy(
    signal_col='ofi_mean_50_reversed',  # Use reversed signal
    entry_threshold=2.0,
    exit_horizon=20,
    stop_loss_pct=0.001,
    take_profit_pct=0.002
)

backtester.print_results(metrics)