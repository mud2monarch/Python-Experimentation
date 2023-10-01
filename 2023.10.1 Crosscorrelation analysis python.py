# packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime

df = pd.read_csv('2023.8.23 PEPE Blocks v2.csv')
df = df.rename(columns={'block_time':'date', 'total_burned_native':'base_fees', 'total_tx_fee_native':'total_fees'})
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S.%f %Z')
df = df.sort_values('date').reset_index(drop=True)

# Add (isolate) priority fees
df['priority_fees']=df['total_fees']-df['base_fees']

# Removing outliers where priority_fees > 15. There are two blocks (out of 50,000) where this is the case. In both instances, it's jaredfromsubway.eth paying a 20ETH priority fee to get inclusion of some random altcoin trade. Don't think there's much signal in retaining these blocks.
outlier_blocks = df[df['priority_fees']>15]
df=df[df['priority_fees']<=15]

# Create a 25 block/5-min rolling average to more smoothly observe fluctuations in gas.
df['ra_base_fees'] = df['base_fees'].rolling(window=25).mean()
df['ra_priority_fees'] = df['priority_fees'].rolling(window=25).mean()
df['ra_total_fees'] = df['total_fees'].rolling(window=25).mean()

# Reorganize
df=df[['date', 'block_number', 'base_fees', 'priority_fees', 'total_fees', 'ra_base_fees', 'ra_priority_fees', 'ra_total_fees', 'total_gas_used', 'gas_limit']]

# Cross-correlational analysis
assert len(df['base_fees']) == len(df['priority_fees']), "length of `base_fees` and `priority_fees` are not the same"

no_offset = df['base_fees'].corr(df['priority_fees'])

correlations = []
correlations_ra=[]

lag_range = range(-200, 400)

for l in lag_range:
    temp_df = df.copy()
    temp_df['priority_fees'] = temp_df['priority_fees'].shift(l)
    correlation = temp_df['base_fees'].corr(temp_df['priority_fees'])
    correlations.append(correlation)
    # do same for rolling average fees
    temp_df['ra_priority_fees'] = temp_df['ra_priority_fees'].shift(l)
    correlation = temp_df['ra_base_fees'].corr(temp_df['ra_priority_fees'])
    correlations_ra.append(correlation)

print (f"Without offset, it's {no_offset} correlation.")

plt.figure(figsize=(10,6))
plt.plot(lag_range, correlations_ra, color ='xkcd:light blue', label = '5 min moving average')
plt.plot(lag_range, correlations, color ='xkcd:mustard', label = 'base data')
plt.xlabel('Offset of priority vs. base (in # of blocks)')
plt.ylabel('Correlation coefficient')
plt.title('Lead/lag of correlations for base vs. priority fees')
plt.legend()

plt.show()