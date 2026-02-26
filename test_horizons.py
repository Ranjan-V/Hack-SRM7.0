import pandas as pd

df = pd.read_csv('data/processed/features_engineered.csv')

print('\n' + '='*70)
print('HORIZON DECAY - FULL DATASET (438k snapshots)')
print('='*70 + '\n')

horizons = [10, 20, 30, 50, 100, 200]
best_feature = 'ofi_mean_50'

print(f'Feature: {best_feature}\n')
print('Horizon | Seconds | Correlation | Strength')
print('-' * 60)

for h in horizons:
    future_return = (df['mid_price'].shift(-h) - df['mid_price']) / df['mid_price']
    corr = df[best_feature].corr(future_return)
    seconds = h / 10
    
    if abs(corr) > 0.10:
        strength = 'STRONG'
    elif abs(corr) > 0.05:
        strength = 'GOOD'
    elif abs(corr) > 0.02:
        strength = 'WEAK'
    else:
        strength = 'NOISE'
    
    print(f'{h:7} | {seconds:7.1f}s | {corr:+.6f} | {strength}')

print('\n' + '='*70 + '\n')