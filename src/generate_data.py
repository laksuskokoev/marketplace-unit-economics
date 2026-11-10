"""Reproducible synthetic marketplace data. Nothing here comes from a real company."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SEED = 20261022

CHANNELS = {
    'Organic': {'n': 1800, 'spend': 180000, 'prob': .56, 'repeat': .43, 'basket': 2100},
    'Search Ads': {'n': 1800, 'spend': 1100000, 'prob': .51, 'repeat': .30, 'basket': 2400},
    'Social Ads': {'n': 1800, 'spend': 1350000, 'prob': .42, 'repeat': .19, 'basket': 1850},
    'Referral': {'n': 1200, 'spend': 270000, 'prob': .60, 'repeat': .48, 'basket': 2300},
}


def generate():
    rng = np.random.default_rng(SEED)
    users = []
    orders = []
    campaigns = []
    user_id = 0
    order_id = 0
    for channel, conf in CHANNELS.items():
        campaigns.append({'channel': channel, 'marketing_spend_rub': conf['spend']})
        for _ in range(conf['n']):
            user_id += 1
            acquired = pd.Timestamp('2026-01-01') + pd.Timedelta(days=int(rng.integers(0, 65)))
            users.append({'user_id': user_id, 'channel': channel, 'acquired_at': acquired.strftime('%Y-%m-%d')})
            if rng.random() >= conf['prob']:
                continue
            n_orders = 1 + int(rng.random() < conf['repeat']) + int(rng.random() < conf['repeat']*.35)
            offsets = sorted(rng.choice(np.arange(1, 91), size=n_orders, replace=False))
            for offset in offsets:
                order_id += 1
                gmv = round(float(np.clip(rng.lognormal(np.log(conf['basket']), .34), 350, 12000)), 2)
                refunded = rng.random() < .085
                orders.append({
                    'order_id': order_id, 'user_id': user_id,
                    'ordered_at': (acquired + pd.Timedelta(days=int(offset))).strftime('%Y-%m-%d'),
                    'gmv_rub': gmv,
                    'status': 'refunded' if refunded else 'fulfilled'
                })
    return pd.DataFrame(users), pd.DataFrame(orders), pd.DataFrame(campaigns)


def main():
    DATA.mkdir(exist_ok=True)
    users, orders, campaigns = generate()
    for name, df in [('users', users), ('orders', orders), ('marketing', campaigns)]:
        df.to_csv(DATA / f'{name}_synthetic.csv', index=False)
        print(f'{name}: {len(df)} rows')

if __name__ == '__main__':
    main()
