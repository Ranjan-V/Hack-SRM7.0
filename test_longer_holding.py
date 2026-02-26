import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

from src.backtest.engine import OFIBacktester
import pandas as pd

df = pd.read_csv('data/processed/features_engineered.csv')
df_test = df.iloc[int(len(df)*0.8):].reset_index(drop=True)

print('\n' + '='*70)
print('TEST: LONGER HOLDING PERIODS')
print('='*70)
print('Hypothesis: Holding longer reduces fee drag\n')
print('Horizon | Seconds | Return   | Win Rate | Sharpe  | Trades')
print('-' * 70)

for horizon in [5000, 10000, 20000, 30000]:
    bt = OFIBacktester(df_test, initial_capital=10000)
    m = bt.run_strategy(
        'ofi_mean_50', 
        entry_threshold=2.0, 
        exit_horizon=horizon, 
        stop_loss_pct=0.005, 
        take_profit_pct=0.01
    )
    if m:
        seconds = horizon / 10
        ret = f"{m['total_return']:+7.2f}%"
        wr = f"{m['win_rate']:5.1f}%"
        sr = f"{m['sharpe_ratio']:7.2f}"
        trades = m['total_trades']
        print(f'{horizon:7} | {seconds:7.1f}s | {ret:8} | {wr:8} | {sr:7} | {trades:6}')

print('\n' + '='*70 + '\n')