"""
Backtesting Engine - Test OFI trading strategy with realistic execution
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple


class OFIBacktester:
    """
    Vectorized backtester for OFI trading strategy
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        initial_capital: float = 10000,
        maker_fee: float = 0.0002,  # 0.02%
        taker_fee: float = 0.0005,  # 0.05%
        slippage_bps: float = 1.0    # 1 basis point
    ):
        """
        Initialize backtester
        
        Args:
            df: DataFrame with features and prices
            initial_capital: Starting capital in USD
            maker_fee: Maker fee as decimal (0.0002 = 0.02%)
            taker_fee: Taker fee as decimal (0.0005 = 0.05%)
            slippage_bps: Slippage in basis points
        """
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.slippage = slippage_bps / 10000  # Convert bps to decimal
        
        self.trades = []
        self.equity_curve = []
        
    def run_strategy(
        self,
        signal_col: str = 'ofi_mean_50',
        entry_threshold: float = 2.0,  # std devs
        exit_horizon: int = 20,  # snapshots (~2 seconds)
        stop_loss_pct: float = 0.001,  # 0.1%
        take_profit_pct: float = 0.002  # 0.2%
    ) -> Dict:
        """
        Run OFI threshold strategy
        
        Strategy:
        - LONG when signal > +entry_threshold std devs
        - SHORT when signal < -entry_threshold std devs
        - Exit after exit_horizon periods OR stop/profit hit
        
        Args:
            signal_col: Column name for OFI signal
            entry_threshold: Entry threshold in standard deviations
            exit_horizon: How long to hold position (in snapshots)
            stop_loss_pct: Stop loss as percentage (0.001 = 0.1%)
            take_profit_pct: Take profit as percentage
        
        Returns:
            Dictionary with performance metrics
        """
        print("\n" + "="*70)
        print("RUNNING OFI BACKTEST")
        print("="*70)
        print(f"Strategy: Threshold-based with {signal_col}")
        print(f"Entry threshold: ±{entry_threshold} std devs")
        print(f"Exit horizon: {exit_horizon} snapshots (~{exit_horizon/10:.1f}s)")
        print(f"Stop loss: {stop_loss_pct*100:.2f}%")
        print(f"Take profit: {take_profit_pct*100:.2f}%")
        print("="*70 + "\n")
        
        # Calculate signal statistics
        signal = self.df[signal_col].values
        signal_mean = np.mean(signal)
        signal_std = np.std(signal)
        
        print(f"Signal statistics:")
        print(f"  Mean: {signal_mean:.6f}")
        print(f"  Std:  {signal_std:.6f}")
        print(f"  Long threshold:  {signal_mean + entry_threshold * signal_std:.6f}")
        print(f"  Short threshold: {signal_mean - entry_threshold * signal_std:.6f}\n")
        
        # Generate signals
        long_signal = signal > (signal_mean + entry_threshold * signal_std)
        short_signal = signal < (signal_mean - entry_threshold * signal_std)
        
        # Track positions
        prices = self.df['mid_price'].values
        position = 0  # 1 = long, -1 = short, 0 = flat
        entry_price = 0
        entry_idx = 0
        capital = self.initial_capital
        
        equity = [capital]
        
        for i in range(len(self.df)):
            current_price = prices[i]
            
            # Check if we should exit current position
            if position != 0:
                # Calculate P&L
                if position == 1:  # Long
                    pnl_pct = (current_price - entry_price) / entry_price
                else:  # Short
                    pnl_pct = (entry_price - current_price) / entry_price
                
                # Exit conditions
                should_exit = False
                exit_reason = ""
                
                # Time-based exit
                if i - entry_idx >= exit_horizon:
                    should_exit = True
                    exit_reason = "time"
                
                # Stop loss
                elif pnl_pct < -stop_loss_pct:
                    should_exit = True
                    exit_reason = "stop_loss"
                
                # Take profit
                elif pnl_pct > take_profit_pct:
                    should_exit = True
                    exit_reason = "take_profit"
                
                if should_exit:
                    # Exit trade
                    exit_price = current_price * (1 - self.slippage * np.sign(position))
                    
                    # Calculate P&L including fees
                    if position == 1:
                        pnl = (exit_price - entry_price) / entry_price
                    else:
                        pnl = (entry_price - exit_price) / entry_price
                    
                    # Subtract fees
                    total_fees = self.taker_fee * 2  # Entry + exit
                    pnl -= total_fees
                    
                    # Update capital
                    capital *= (1 + pnl)
                    
                    # Record trade
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
            
            # Check for new entry signals (only if flat)
            if position == 0:
                if long_signal[i]:
                    position = 1
                    entry_price = current_price * (1 + self.slippage)
                    entry_idx = i
                elif short_signal[i]:
                    position = -1
                    entry_price = current_price * (1 - self.slippage)
                    entry_idx = i
            
            equity.append(capital)
        
        self.equity_curve = equity
        
        # Calculate performance metrics
        metrics = self._calculate_metrics()
        
        return metrics
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        
        if len(self.trades) == 0:
            print("⚠ No trades executed!")
            return {}
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic stats
        total_trades = len(trades_df)
        winning_trades = (trades_df['pnl_pct'] > 0).sum()
        losing_trades = (trades_df['pnl_pct'] < 0).sum()
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # P&L stats
        total_return = (self.equity_curve[-1] / self.initial_capital - 1) * 100
        avg_trade_pnl = trades_df['pnl_pct'].mean()
        
        winning_pnl = trades_df[trades_df['pnl_pct'] > 0]['pnl_pct'].mean() if winning_trades > 0 else 0
        losing_pnl = trades_df[trades_df['pnl_pct'] < 0]['pnl_pct'].mean() if losing_trades > 0 else 0
        
        # Risk metrics
        equity_series = pd.Series(self.equity_curve)
        returns = equity_series.pct_change().dropna()
        
        sharpe_ratio = np.sqrt(252 * 24 * 60 * 6) * returns.mean() / returns.std() if returns.std() > 0 else 0
        # Annualization: 252 days * 24 hours * 60 min * 6 (10-sec periods per min)
        
        # Drawdown
        cummax = equity_series.expanding().max()
        drawdown = (equity_series - cummax) / cummax
        max_drawdown = drawdown.min() * 100
        
        # Exit reasons
        exit_counts = trades_df['exit_reason'].value_counts()
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate * 100,
            'total_return': total_return,
            'avg_trade_pnl': avg_trade_pnl,
            'avg_win': winning_pnl,
            'avg_loss': losing_pnl,
            'profit_factor': abs(winning_pnl * winning_trades / (losing_pnl * losing_trades)) if losing_trades > 0 else np.inf,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'exit_reasons': exit_counts.to_dict(),
            'final_capital': self.equity_curve[-1]
        }
        
        return metrics
    
    def print_results(self, metrics: Dict):
        """Print backtest results"""
        
        if not metrics:
            return
        
        print("\n" + "="*70)
        print("BACKTEST RESULTS")
        print("="*70 + "\n")
        
        print("Trading Performance:")
        print(f"  Total trades:       {metrics['total_trades']:>6}")
        print(f"  Winning trades:     {metrics['winning_trades']:>6} ({metrics['win_rate']:.1f}%)")
        print(f"  Losing trades:      {metrics['losing_trades']:>6}")
        print()
        
        print("Returns:")
        print(f"  Total return:       {metrics['total_return']:>6.2f}%")
        print(f"  Avg trade P&L:      {metrics['avg_trade_pnl']:>6.3f}%")
        print(f"  Avg winning trade:  {metrics['avg_win']:>6.3f}%")
        print(f"  Avg losing trade:   {metrics['avg_loss']:>6.3f}%")
        print(f"  Profit factor:      {metrics['profit_factor']:>6.2f}")
        print()
        
        print("Risk Metrics:")
        print(f"  Sharpe ratio:       {metrics['sharpe_ratio']:>6.2f}")
        print(f"  Max drawdown:       {metrics['max_drawdown']:>6.2f}%")
        print()
        
        print("Capital:")
        print(f"  Initial:            ${self.initial_capital:>10,.2f}")
        print(f"  Final:              ${metrics['final_capital']:>10,.2f}")
        print()
        
        print("Exit Reasons:")
        for reason, count in metrics['exit_reasons'].items():
            pct = count / metrics['total_trades'] * 100
            print(f"  {reason:15}     {count:>6} ({pct:.1f}%)")
        
        print("\n" + "="*70)
        
        # Verdict
        if metrics['sharpe_ratio'] > 2 and metrics['win_rate'] > 50:
            print("✅ EXCELLENT STRATEGY - Sharpe > 2 and Win Rate > 50%")
        elif metrics['sharpe_ratio'] > 1 and metrics['win_rate'] > 48:
            print("✅ GOOD STRATEGY - Positive Sharpe and decent win rate")
        elif metrics['total_return'] > 0:
            print("⚠ MARGINAL STRATEGY - Profitable but low Sharpe")
        else:
            print("❌ LOSING STRATEGY - Negative returns")
        
        print("="*70 + "\n")


def run_backtest_analysis(
    features_file: str = "data/processed/features_engineered.csv",
    test_size: float = 0.2
):
    """
    Run comprehensive backtest analysis
    """
    print("\n" + "="*70)
    print("LOADING DATA FOR BACKTEST")
    print("="*70 + "\n")
    
    # Load features
    df = pd.read_csv(features_file)
    print(f"Loaded {len(df):,} rows")
    
    # Use only test set (out-of-sample)
    split_idx = int(len(df) * (1 - test_size))
    df_test = df.iloc[split_idx:].reset_index(drop=True)
    
    print(f"Using test set: {len(df_test):,} rows (last {test_size*100:.0f}%)")
    print(f"Time range: {df_test['timestamp'].min()} to {df_test['timestamp'].max()}")
    print()
    
    # Initialize backtester
    backtester = OFIBacktester(
        df_test,
        initial_capital=10000,
        maker_fee=0.0002,
        taker_fee=0.0005,
        slippage_bps=1.0
    )
    
    # Run strategy
    metrics = backtester.run_strategy(
        signal_col='ofi_mean_50',
        entry_threshold=2.0,
        exit_horizon=20,  # ~2 seconds
        stop_loss_pct=0.001,
        take_profit_pct=0.002
    )
    
    # Print results
    backtester.print_results(metrics)
    
    return backtester, metrics


if __name__ == "__main__":
    backtester, metrics = run_backtest_analysis()