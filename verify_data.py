"""
Data Verification Script - Check quality of collected order book data
Run this after data collection to verify everything is ready for analysis
"""
import pandas as pd
import glob
from pathlib import Path
from datetime import datetime
import numpy as np


def verify_data():
    """
    Comprehensive data verification and quality check
    """
    print("\n" + "="*70)
    print("ORDER BOOK DATA VERIFICATION")
    print("="*70 + "\n")
    
    # Find all CSV files
    data_dir = Path("data/raw")
    files = sorted(glob.glob(str(data_dir / "BTCUSDT*.csv")))
    
    if not files:
        print("❌ No data files found in data/raw/")
        print("   Make sure you collected data first!")
        return
    
    print(f"📁 Found {len(files)} data file(s)\n")
    
    # Analyze each file
    file_stats = []
    total_rows = 0
    
    for i, filepath in enumerate(files, 1):
        try:
            df = pd.read_csv(filepath)
            filename = Path(filepath).name
            
            file_info = {
                'number': i,
                'filename': filename,
                'rows': len(df),
                'size_mb': Path(filepath).stat().st_size / (1024**2),
                'start_time': df['timestamp'].iloc[0] if len(df) > 0 else None,
                'end_time': df['timestamp'].iloc[-1] if len(df) > 0 else None,
                'nulls': df.isnull().sum().sum()
            }
            
            file_stats.append(file_info)
            total_rows += len(df)
            
            # Print file info
            print(f"{i}. {filename[:50]:<50}")
            print(f"   Rows: {len(df):>8,} | Size: {file_info['size_mb']:>6.2f} MB")
            if file_info['start_time'] and file_info['end_time']:
                print(f"   Time: {file_info['start_time'][:19]} → {file_info['end_time'][:19]}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error reading file: {e}\n")
    
    print("="*70)
    print(f"📊 TOTAL SNAPSHOTS: {total_rows:,}")
    print(f"💾 TOTAL SIZE: {sum([f['size_mb'] for f in file_stats]):.2f} MB")
    print("="*70 + "\n")
    
    # Load all data for quality checks
    print("🔍 Running Quality Checks...\n")
    
    try:
        # Load all files
        print("   Loading all data files... ", end="", flush=True)
        dfs = [pd.read_csv(f) for f in files]
        df_all = pd.concat(dfs, ignore_index=True)
        print("✓")
        
        # Check for duplicates
        print("   Checking for duplicate timestamps... ", end="", flush=True)
        duplicates = df_all.duplicated(subset=['unix_ms']).sum()
        print(f"{'✓' if duplicates == 0 else '⚠'} ({duplicates:,} found)")
        
        # Check for null values
        print("   Checking for null values... ", end="", flush=True)
        nulls = df_all.isnull().sum().sum()
        print(f"{'✓' if nulls == 0 else '⚠'} ({nulls:,} found)")
        
        # Check data continuity
        print("   Checking time continuity... ", end="", flush=True)
        df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
        time_gaps = df_all['timestamp'].diff().dt.total_seconds()
        large_gaps = (time_gaps > 5).sum()  # Gaps larger than 5 seconds
        print(f"{'✓' if large_gaps == 0 else '⚠'} ({large_gaps:,} gaps > 5s)")
        
        # Price statistics
        print("\n" + "="*70)
        print("📈 MARKET STATISTICS")
        print("="*70 + "\n")
        
        print(f"Price Range:")
        print(f"   Min:     ${df_all['mid_price'].min():>10,.2f}")
        print(f"   Max:     ${df_all['mid_price'].max():>10,.2f}")
        print(f"   Mean:    ${df_all['mid_price'].mean():>10,.2f}")
        print(f"   Std Dev: ${df_all['mid_price'].std():>10,.2f}")
        
        print(f"\nSpread Statistics:")
        print(f"   Avg Spread:     {df_all['spread_pct'].mean()*100:>8.4f}%")
        print(f"   Min Spread:     {df_all['spread_pct'].min()*100:>8.4f}%")
        print(f"   Max Spread:     {df_all['spread_pct'].max()*100:>8.4f}%")
        
        print(f"\nBook Imbalance:")
        print(f"   Mean:           {df_all['book_imbalance'].mean():>8.4f}")
        print(f"   Std Dev:        {df_all['book_imbalance'].std():>8.4f}")
        
        # Time coverage
        print(f"\nTime Coverage:")
        start = df_all['timestamp'].min()
        end = df_all['timestamp'].max()
        duration = (end - start).total_seconds() / 3600
        print(f"   Start:    {start}")
        print(f"   End:      {end}")
        print(f"   Duration: {duration:.2f} hours ({duration/24:.2f} days)")
        
        # Data completeness
        print(f"\nData Completeness:")
        expected_snapshots = duration * 3600 * 10  # 10 snapshots per second
        completeness = (len(df_all) / expected_snapshots) * 100
        print(f"   Expected:  {expected_snapshots:>10,.0f} snapshots (at 10/sec)")
        print(f"   Actual:    {len(df_all):>10,} snapshots")
        print(f"   Coverage:  {completeness:>10,.1f}%")
        
        # Final verdict
        print("\n" + "="*70)
        print("VERIFICATION RESULT")
        print("="*70 + "\n")
        
        issues = []
        if nulls > 0:
            issues.append(f"⚠ {nulls:,} null values found")
        if large_gaps > 0:
            issues.append(f"⚠ {large_gaps:,} time gaps > 5 seconds")
        if completeness < 80:
            issues.append(f"⚠ Data coverage only {completeness:.1f}%")
        
        if not issues:
            print("✅ ALL CHECKS PASSED!")
            print("\nYour data is ready for feature engineering! 🚀")
            print("\nNext steps:")
            print("  1. Run feature engineering pipeline")
            print("  2. Calculate OFI features")
            print("  3. Train predictive models")
            print("  4. Backtest strategy")
        else:
            print("⚠ ISSUES DETECTED:\n")
            for issue in issues:
                print(f"   {issue}")
            print("\nData is still usable, but some gaps/issues present.")
        
        print("\n" + "="*70 + "\n")
        
        # Save summary
        summary_file = data_dir / "data_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Data Collection Summary\n")
            f.write(f"="*50 + "\n\n")
            f.write(f"Total Files: {len(files)}\n")
            f.write(f"Total Snapshots: {total_rows:,}\n")
            f.write(f"Total Size: {sum([fs['size_mb'] for fs in file_stats]):.2f} MB\n")
            f.write(f"Time Range: {start} to {end}\n")
            f.write(f"Duration: {duration:.2f} hours\n")
            f.write(f"Price Range: ${df_all['mid_price'].min():.2f} - ${df_all['mid_price'].max():.2f}\n")
            f.write(f"Avg Spread: {df_all['spread_pct'].mean()*100:.4f}%\n")
        
        print(f"📄 Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"\n❌ Error during quality checks: {e}")
        print("   Individual files may still be valid.")


if __name__ == "__main__":
    verify_data()