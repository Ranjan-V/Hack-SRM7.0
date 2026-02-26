"""
Run Feature Engineering Pipeline
Quick script to process all your collected data
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from src.features.engineer import FeatureEngineer
import pandas as pd
import numpy as np


def run_full_pipeline(sample_size: int = None):
    """
    Run complete feature engineering on your data
    
    Args:
        sample_size: Number of rows to process (None = all 438k rows)
    """
    print("\n" + "="*70)
    print("OFI FEATURE ENGINEERING PIPELINE")
    print("="*70)
    print("This will process your collected order book data and create")
    print("ML-ready features for prediction models.")
    print("="*70 + "\n")
    
    if sample_size:
        print(f"⚠ Running on SAMPLE: {sample_size:,} rows (for testing)")
    else:
        print(f"✓ Running on FULL dataset (~438k rows)")
    
    print("\nThis will take 2-5 minutes...\n")
    
    # Initialize feature engineer
    fe = FeatureEngineer(data_dir="data/raw")
    
    # Load data
    df = fe.load_data(nrows=sample_size)
    
    # Engineer features
    # Prediction horizon: 50 snapshots ≈ 5 seconds
    features, targets = fe.engineer_features(prediction_horizon=50)
    
    # Create train/test split
    X_train, X_test, y_train, y_test, feature_cols = fe.create_training_dataset(
        test_size=0.2,
        remove_outliers=True
    )
    
    # Save to disk
    output_file = fe.save_features()
    
    # Calculate some basic statistics
    print("\n" + "="*70)
    print("FEATURE ANALYSIS")
    print("="*70 + "\n")
    
    print("Target Distribution (y_train):")
    print(f"  Mean return: {y_train.mean()*100:.4f}%")
    print(f"  Std dev: {y_train.std()*100:.4f}%")
    print(f"  Min: {y_train.min()*100:.4f}%")
    print(f"  Max: {y_train.max()*100:.4f}%")
    
    # Directional accuracy if random
    print(f"\nDirectional Bias:")
    positive_pct = (y_train > 0).sum() / len(y_train) * 100
    print(f"  Positive returns: {positive_pct:.1f}%")
    print(f"  Negative returns: {100-positive_pct:.1f}%")
    print(f"  → Random guess accuracy: {max(positive_pct, 100-positive_pct):.1f}%")
    
    # Feature statistics
    print(f"\nFeature Statistics:")
    print(f"  Total features: {len(feature_cols)}")
    
    # Group features by type
    ofi_features = [f for f in feature_cols if 'ofi' in f]
    book_features = [f for f in feature_cols if any(x in f for x in ['spread', 'volume', 'depth', 'microprice'])]
    price_features = [f for f in feature_cols if 'return' in f or 'volatility' in f or 'price_vs' in f]
    time_features = [f for f in feature_cols if any(x in f for x in ['hour', 'minute', 'is_'])]
    
    print(f"    OFI features: {len(ofi_features)}")
    print(f"    Book features: {len(book_features)}")
    print(f"    Price features: {len(price_features)}")
    print(f"    Time features: {len(time_features)}")
    
    # Show top features by variance (most "active")
    print(f"\nMost Variable Features (Top 10):")
    feature_variance = X_train.var().sort_values(ascending=False).head(10)
    for i, (feat, var) in enumerate(feature_variance.items(), 1):
        print(f"  {i:2}. {feat:20} | Variance: {var:.6f}")
    
    print("\n" + "="*70)
    print("✅ FEATURE ENGINEERING COMPLETE!")
    print("="*70)
    print(f"\nYour data is ready for modeling!")
    print(f"  Features saved: {output_file}")
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Test samples: {len(X_test):,}")
    
    print("\nNext steps:")
    print("  1. Analyze feature importance (correlation with returns)")
    print("  2. Train predictive models (XGBoost, LightGBM)")
    print("  3. Backtest trading strategy")
    print("  4. Write research paper!")
    
    print("\n" + "="*70 + "\n")
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'features': feature_cols,
        'output_file': output_file
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run feature engineering pipeline')
    parser.add_argument('--sample', type=int, default=None,
                       help='Number of rows to process (default: all)')
    parser.add_argument('--full', action='store_true',
                       help='Process full dataset (all 438k rows)')
    
    args = parser.parse_args()
    
    if args.full:
        sample_size = None
        print("\n🚀 Processing FULL dataset (this may take 5-10 minutes)...\n")
    elif args.sample:
        sample_size = args.sample
        print(f"\n⚡ Processing SAMPLE of {sample_size:,} rows (for testing)...\n")
    else:
        # Default: process 50k rows for quick testing
        sample_size = 50000
        print(f"\n⚡ Processing SAMPLE of {sample_size:,} rows (for testing)...")
        print("   Use --full to process all 438k rows\n")
    
    results = run_full_pipeline(sample_size=sample_size)
    
    print("\n✅ Done! Results stored in 'results' dictionary")
    print("   Access with: results['X_train'], results['y_train'], etc.\n")