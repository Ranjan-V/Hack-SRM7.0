"""
ML-Based Trading Strategy Backtest
Uses XGBoost predictions instead of simple thresholds
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.train_model import train_and_evaluate
from src.backtest.engine import OFIBacktester
import pandas as pd
import numpy as np


def run_ml_backtest():
    """
    Train ML model and backtest using its predictions
    """
    print("\n" + "="*70)
    print("ML-BASED OFI TRADING STRATEGY")
    print("="*70)
    print("Step 1: Train XGBoost model")
    print("Step 2: Backtest using ML predictions")
    print("="*70 + "\n")
    
    # Step 1: Train model
    trainer, results = train_and_evaluate(
        for_classification=True,
        test_size=0.2
    )
    
    # Step 2: Prepare test data with ML predictions
    df_test = trainer.df_test.copy()
    
    # ML predictions: 1 = UP, 0 = DOWN
    # Convert to signal: +1 for UP, -1 for DOWN
    df_test['ml_signal'] = df_test['ml_prediction'].apply(lambda x: 1 if x == 1 else -1)
    
    # Get prediction probabilities for confidence-based trading
    if hasattr(trainer.model, 'predict_proba'):
        probas = trainer.model.predict_proba(
            df_test[[c for c in df_test.columns 
                    if c not in ['timestamp', 'symbol', 'unix_ms', 'return_50', 
                                'direction_50', 'mid_price', 'ml_prediction', 'ml_signal']]].values
        )
        df_test['ml_confidence'] = np.abs(probas[:, 1] - 0.5) * 2  # 0 to 1 scale
    else:
        df_test['ml_confidence'] = 1.0
    
    print("\n" + "="*70)
    print("RUNNING ML-BASED BACKTEST")
    print("="*70)
    print("Strategy: Trade based on XGBoost predictions")
    print("  BUY when model predicts UP")
    print("  SELL when model predicts DOWN")
    print("  Only trade when confidence > threshold")
    print("="*70 + "\n")
    
    # Initialize backtester
    backtester = MLBacktester(
        df_test,
        initial_capital=10000,
        maker_fee=0.0002,
        taker_fee=0.0005,
        slippage_bps=1.0
    )
    
    # Run ML strategy
    metrics = backtester.run_ml_strategy(
        confidence_threshold=0.3,  # Only trade when >30% confident
        exit_horizon=20,
        stop_loss_pct=0.001,
        take_profit_pct=0.002
    )
    
    # Print results
    backtester.print_results(metrics)
    
    # Compare to baseline
    print("\n" + "="*70)
    print("COMPARISON TO SIMPLE THRESHOLD STRATEGY")
    print("="*70 + "\n")
    
    # Run baseline for comparison
    backtester_baseline = OFIBacktester(df_test, initial_capital=10000)
    metrics_baseline = backtester_baseline.run_strategy(
        signal_col='ofi_mean_50',
        entry_threshold=2.0,
        exit_horizon=20
    )
    
    print("\nBaseline (threshold) results:")
    print(f"  Total return: {metrics_baseline.get('total_return', 0):.2f}%")
    print(f"  Win rate: {metrics_baseline.get('win_rate', 0):.1f}%")
    print(f"  Sharpe: {metrics_baseline.get('sharpe_ratio', 0):.2f}")
    
    print(f"\nML strategy results:")
    print(f"  Total return: {metrics['total_return']:.2f}%")
    print(f"  Win rate: {metrics['win_rate']:.1f}%")
    print(f"  Sharpe: {metrics['sharpe_ratio']:.2f}")
    
    improvement = metrics['total_return'] - metrics_baseline.get('total_return', 0)
    print(f"\nImprovement: {improvement:+.2f}%")
    
    print("\n" + "="*70 + "\n")
    
    return backtester, metrics


class MLBacktester(OFIBacktester):
    """
    Extended backtester that uses ML predictions
    """
    
    def run_ml_strategy(
        self,
        confidence_threshold: float = 0.3,
        exit_horizon: int = 20,
        stop_loss_pct: float = 0.001,
        take_profit_pct: float = 0.002
    ):
        """
        Trade based on ML model predictions
        """
        print(f"ML Strategy Parameters:")
        print(f"  Confidence threshold: {confidence_threshold:.2f}")
        print(f"  Exit horizon: {exit_horizon} snapshots (~{exit_horizon/10:.1f}s)")
        print(f"  Stop loss: {stop_loss_pct*100:.2f}%")
        print(f"  Take profit: {take_profit_pct*100:.2f}%\n")
        
        # Get signals
        signals = self.df['ml_signal'].values
        confidences = self.df['ml_confidence'].values if 'ml_confidence' in self.df.columns else np.ones(len(self.df))
        prices = self.df['mid_price'].values
        
        # Track positions
        position = 0
        entry_price = 0
        entry_idx = 0
        capital = self.initial_capital
        
        equity = [capital]
        trades_taken = 0
        trades_skipped = 0
        
        for i in range(len(self.df)):
            current_price = prices[i]
            
            # Check if we should exit
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
            
            # Check for new entries
            if position == 0 and i < len(signals):
                # Only trade if confidence is high enough
                if confidences[i] >= confidence_threshold:
                    if signals[i] == 1:  # ML predicts UP
                        position = 1
                        entry_price = current_price * (1 + self.slippage)
                        entry_idx = i
                        trades_taken += 1
                    elif signals[i] == -1:  # ML predicts DOWN
                        position = -1
                        entry_price = current_price * (1 - self.slippage)
                        entry_idx = i
                        trades_taken += 1
                else:
                    trades_skipped += 1
            
            equity.append(capital)
        
        self.equity_curve = equity
        
        print(f"Trade filtering:")
        print(f"  Trades taken: {trades_taken}")
        print(f"  Trades skipped (low confidence): {trades_skipped}")
        print(f"  Filter rate: {trades_skipped/(trades_taken+trades_skipped)*100:.1f}%\n")
        
        metrics = self._calculate_metrics()
        return metrics


if __name__ == "__main__":
    # Install xgboost if needed
    try:
        import xgboost
        import joblib
    except ImportError:
        print("\n⚠ Missing dependencies!")
        print("   Run: pip install xgboost joblib scikit-learn")
        print()
        sys.exit(1)
    
    backtester, metrics = run_ml_backtest()
    
    print("\n✅ ML backtest complete!")
    print("   XGBoost learned when OFI signals are reliable")
    print("   Strategy adapts to market conditions\n")