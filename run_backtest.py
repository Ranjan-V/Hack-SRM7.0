"""
Run OFI Trading Strategy Backtest
Tests profitability after realistic fees and slippage
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.backtest.engine import run_backtest_analysis

if __name__ == "__main__":
    print("\n" + "="*70)
    print("OFI TRADING STRATEGY BACKTEST")
    print("="*70)
    print("Testing strategy on out-of-sample data (last 20% of dataset)")
    print("="*70 + "\n")
    
    # Run backtest
    backtester, metrics = run_backtest_analysis(
        features_file="data/processed/features_engineered.csv",
        test_size=0.2
    )
    
    print("\n📊 Backtest complete!")
    print("="*70 + "\n")