"""
Test Reversed (SHORT) Strategy
Theory: During downtrends, fade the OFI signal
- When OFI says UP → SHORT (fade the buying pressure)
- When OFI says DOWN → LONG (fade the selling pressure)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backtest.engine import OFIBacktester
import pandas as pd
import numpy as np


def test_reversed_strategies():
    """
    Test multiple reversed strategies
    """
    print("\n" + "="*70)
    print("TESTING REVERSED (SHORT-BIAS) STRATEGIES")
    print("="*70)
    print("Hypothesis: During downtrend, OFI signals work in REVERSE")
    print("="*70 + "\n")
    
    # Load data
    df = pd.read_csv('data/processed/features_engineered.csv')
    split_idx = int(len(df) * 0.8)
    df_test = df.iloc[split_idx:].reset_index(drop=True).copy()
    
    print(f"Test period: {df_test['timestamp'].min()} → {df_test['timestamp'].max()}")
    print(f"Test samples: {len(df_test):,}\n")
    
    results = {}
    
    # Strategy 1: Simple OFI reversal
    print("\n" + "="*70)
    print("STRATEGY 1: REVERSED OFI THRESHOLD")
    print("="*70)
    print("SHORT when ofi_mean_50 > threshold (fade buying pressure)")
    print("LONG when ofi_mean_50 < threshold (fade selling pressure)")
    print("="*70 + "\n")
    
    df_test['ofi_reversed'] = -df_test['ofi_mean_50']
    
    bt1 = OFIBacktester(df_test, initial_capital=10000)
    m1 = bt1.run_strategy(
        signal_col='ofi_reversed',
        entry_threshold=2.0,
        exit_horizon=20,
        stop_loss_pct=0.001,
        take_profit_pct=0.002
    )
    bt1.print_results(m1)
    results['reversed_threshold'] = m1
    
    # Strategy 2: ML predictions reversed
    print("\n" + "="*70)
    print("STRATEGY 2: REVERSED ML PREDICTIONS")
    print("="*70)
    print("Do OPPOSITE of what XGBoost predicts")
    print("="*70 + "\n")
    
    if 'ml_prediction' in df_test.columns:
        # Reverse ML predictions
        df_test['ml_reversed'] = 1 - df_test['ml_prediction']
        df_test['ml_signal_reversed'] = df_test['ml_reversed'].apply(lambda x: 1 if x == 1 else -1)
        
        # Create reversed confidence signal
        signal_mean = df_test['ofi_mean_50'].mean()
        signal_std = df_test['ofi_mean_50'].std()
        
        # HIGH confidence when ML is confident (but we reverse the direction)
        df_test['ml_confidence_reversed'] = df_test.get('ml_confidence', 1.0)
        
        bt2 = MLReversedBacktester(df_test, initial_capital=10000)
        m2 = bt2.run_ml_reversed_strategy(
            confidence_threshold=0.3,
            exit_horizon=20,
            stop_loss_pct=0.001,
            take_profit_pct=0.002
        )
        bt2.print_results(m2)
        results['reversed_ml'] = m2
    else:
        print("⚠ No ML predictions found. Run train_model.py first.\n")
        results['reversed_ml'] = None
    
    # Strategy 3: Adaptive (use correlation sign)
    print("\n" + "="*70)
    print("STRATEGY 3: ADAPTIVE BASED ON RECENT CORRELATION")
    print("="*70)
    print("Check if OFI-return correlation is positive or negative")
    print("Trade accordingly")
    print("="*70 + "\n")
    
    bt3 = AdaptiveBacktester(df_test, initial_capital=10000)
    m3 = bt3.run_adaptive_strategy(
        lookback=500,  # Check last 500 snapshots
        entry_threshold=2.0,
        exit_horizon=20
    )
    bt3.print_results(m3)
    results['adaptive'] = m3
    
    # Summary comparison
    print("\n" + "="*70)
    print("STRATEGY COMPARISON")
    print("="*70 + "\n")
    
    strategies = [
        ('Original (LONG bias)', None),  # We know this lost -63%
        ('Reversed Threshold', results['reversed_threshold']),
        ('Reversed ML', results['reversed_ml']),
        ('Adaptive', results['adaptive'])
    ]
    
    print(f"{'Strategy':<25} | {'Return':<10} | {'Win Rate':<10} | {'Sharpe':<10} | {'Trades'}")
    print("-" * 80)
    
    print(f"{'Original (LONG bias)':<25} | {'-63.04%':<10} | {'0.0%':<10} | {'-146.76':<10} | {'875'}")
    
    for name, metrics in strategies[1:]:
        if metrics:
            ret = f"{metrics['total_return']:+.2f}%"
            wr = f"{metrics['win_rate']:.1f}%"
            sr = f"{metrics['sharpe_ratio']:.2f}"
            trades = str(metrics['total_trades'])
            print(f"{name:<25} | {ret:<10} | {wr:<10} | {sr:<10} | {trades}")
    
    print("\n" + "="*70)
    
    # Find best strategy
    best_strategy = None
    best_return = -100
    
    for name, metrics in strategies[1:]:
        if metrics and metrics['total_return'] > best_return:
            best_return = metrics['total_return']
            best_strategy = name
    
    if best_return > 0:
        print(f"✅ WINNER: {best_strategy}")
        print(f"   Return: {best_return:+.2f}%")
        print(f"   Strategy is PROFITABLE!")
    elif best_return > -20:
        print(f"⚠ BEST: {best_strategy}")
        print(f"   Return: {best_return:+.2f}%")
        print(f"   Better but still losing")
    else:
        print(f"❌ ALL STRATEGIES LOSE MONEY")
        print(f"   Best return: {best_return:+.2f}%")
        print(f"   Market regime too strong!")
    
    print("="*70 + "\n")
    
    return results


class MLReversedBacktester(OFIBacktester):
    """Backtest with REVERSED ML predictions"""
    
    def run_ml_reversed_strategy(self, confidence_threshold=0.3, exit_horizon=20, 
                                 stop_loss_pct=0.001, take_profit_pct=0.002):
        """Trade OPPOSITE of ML predictions"""
        
        signals = self.df['ml_signal_reversed'].values
        confidences = self.df['ml_confidence_reversed'].values if 'ml_confidence_reversed' in self.df.columns else np.ones(len(self.df))
        prices = self.df['mid_price'].values
        
        position = 0
        entry_price = 0
        entry_idx = 0
        capital = self.initial_capital
        equity = [capital]
        
        for i in range(len(self.df)):
            current_price = prices[i]
            
            if position != 0:
                if position == 1:
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                
                should_exit = False
                exit_reason = ""
                
                if i - entry_idx >= exit_horizon:
                    should_exit = True
                    exit_reason = "time"
                elif pnl_pct < -stop_loss_pct:
                    should_exit = True
                    exit_reason = "stop_loss"
                elif pnl_pct > take_profit_pct:
                    should_exit = True
                    exit_reason = "take_profit"
                
                if should_exit:
                    exit_price = current_price * (1 - self.slippage * np.sign(position))
                    
                    if position == 1:
                        pnl = (exit_price - entry_price) / entry_price
                    else:
                        pnl = (entry_price - exit_price) / entry_price
                    
                    pnl -= self.taker_fee * 2
                    capital *= (1 + pnl)
                    
                    self.trades.append({
                        'entry_idx': entry_idx,
                        'exit_idx': i,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'position': 'LONG' if position == 1 else 'SHORT',
                        'pnl_pct': pnl * 100,
                        'exit_reason': exit_reason,
                        'holding_period': i - entry_idx
                    })
                    
                    position = 0
            
            if position == 0 and i < len(signals):
                if confidences[i] >= confidence_threshold:
                    if signals[i] == 1:
                        position = 1
                        entry_price = current_price * (1 + self.slippage)
                        entry_idx = i
                    elif signals[i] == -1:
                        position = -1
                        entry_price = current_price * (1 - self.slippage)
                        entry_idx = i
            
            equity.append(capital)
        
        self.equity_curve = equity
        return self._calculate_metrics()


class AdaptiveBacktester(OFIBacktester):
    """Adapts signal direction based on recent correlation"""
    
    def run_adaptive_strategy(self, lookback=500, entry_threshold=2.0, 
                             exit_horizon=20, stop_loss_pct=0.001, take_profit_pct=0.002):
        """Check recent correlation and adapt"""
        
        print("Adaptive strategy:")
        print(f"  Lookback window: {lookback} snapshots (~{lookback/10:.0f}s)")
        print(f"  Recalculates correlation every {lookback} snapshots")
        print(f"  Trades in direction of correlation\n")
        
        signal = self.df['ofi_mean_50'].values
        prices = self.df['mid_price'].values
        returns = np.diff(prices) / prices[:-1]
        returns = np.concatenate([[0], returns])
        
        position = 0
        entry_price = 0
        entry_idx = 0
        capital = self.initial_capital
        equity = [capital]
        
        signal_mean = np.mean(signal)
        signal_std = np.std(signal)
        
        for i in range(lookback, len(self.df)):
            current_price = prices[i]
            
            # Calculate recent correlation
            recent_signal = signal[i-lookback:i]
            recent_returns = returns[i-lookback:i]
            recent_corr = np.corrcoef(recent_signal, recent_returns)[0, 1]
            
            # Decide direction based on correlation sign
            signal_multiplier = 1 if recent_corr > 0 else -1
            
            if position != 0:
                if position == 1:
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                
                should_exit = False
                exit_reason = ""
                
                if i - entry_idx >= exit_horizon:
                    should_exit = True
                    exit_reason = "time"
                elif pnl_pct < -stop_loss_pct:
                    should_exit = True
                    exit_reason = "stop_loss"
                elif pnl_pct > take_profit_pct:
                    should_exit = True
                    exit_reason = "take_profit"
                
                if should_exit:
                    exit_price = current_price * (1 - self.slippage * np.sign(position))
                    
                    if position == 1:
                        pnl = (exit_price - entry_price) / entry_price
                    else:
                        pnl = (entry_price - exit_price) / entry_price
                    
                    pnl -= self.taker_fee * 2
                    capital *= (1 + pnl)
                    
                    self.trades.append({
                        'entry_idx': entry_idx,
                        'exit_idx': i,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'position': 'LONG' if position == 1 else 'SHORT',
                        'pnl_pct': pnl * 100,
                        'exit_reason': exit_reason,
                        'holding_period': i - entry_idx
                    })
                    
                    position = 0
            
            if position == 0:
                adjusted_signal = signal[i] * signal_multiplier
                
                if adjusted_signal > signal_mean + entry_threshold * signal_std:
                    position = 1
                    entry_price = current_price * (1 + self.slippage)
                    entry_idx = i
                elif adjusted_signal < signal_mean - entry_threshold * signal_std:
                    position = -1
                    entry_price = current_price * (1 - self.slippage)
                    entry_idx = i
            
            equity.append(capital)
        
        self.equity_curve = equity
        return self._calculate_metrics()


if __name__ == "__main__":
    results = test_reversed_strategies()