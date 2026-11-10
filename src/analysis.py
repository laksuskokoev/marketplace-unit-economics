"""90-day contribution economics from synthetic marketplace events.

All users have 90 days of complete observation. 'LTV90' below means
observed 90-day contribution per acquired user, *not* lifetime revenue.
"""
from pathlib import Path
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'reports'
FIG = ROOT / 'figures'
COMMISSION_RATE = 0.15
DELIVERY_FEE = 35.0
PAYMENT_RATE = 0.022
FULFILLMENT_COST = 65.0
SUPPORT_COST = 12.0
REFUND_HANDLING_COST = 45.0


def enrich_orders(users, orders):
    result = orders.merge(users[['user_id', 'channel', 'acquired_at']], on='user_id', how='left', validate='many_to_one')
    if result['channel'].isna().any():
        raise ValueError('Order references an unknown user')
    result['age_days'] = (pd.to_datetime(result['ordered_at']) - pd.to_datetime(result['acquired_at'])).dt.days
    if not result['age_days'].between(0, 90).all():
        raise ValueError('Orders outside 90-day measurement window')
    delivered = result['status'].eq('fulfilled')
    if not result['status'].isin(['fulfilled', 'refunded']).all():
        raise ValueError('Unknown order status')
    result['net_gmv_rub'] = np.where(delivered, result['gmv_rub'], 0.0)
    result['marketplace_revenue_rub'] = np.where(delivered, result['gmv_rub'] * COMMISSION_RATE + DELIVERY_FEE, 0.0)
    result['variable_cost_rub'] = np.where(delivered, result['gmv_rub'] * PAYMENT_RATE + FULFILLMENT_COST + SUPPORT_COST, REFUND_HANDLING_COST)
    result['contribution_rub'] = result['marketplace_revenue_rub'] - result['variable_cost_rub']
    return result


def calculate(users, orders, marketing):
    if users['user_id'].duplicated().any() or orders['order_id'].duplicated().any() or marketing['channel'].duplicated().any():
        raise ValueError('Duplicate entity identifiers')
    if set(users['channel']) != set(marketing['channel']):
        raise ValueError('Missing marketing channel budget')
    events = enrich_orders(users, orders)
    base = users.groupby('channel', as_index=False).agg(acquired_users=('user_id', 'nunique'))
    buyers = events.loc[events['status'].eq('fulfilled')].groupby('channel')['user_id'].nunique().rename('buyers')
    rolled = events.groupby('channel').agg(
        orders=('order_id', 'size'), fulfilled_orders=('status', lambda x: int((x == 'fulfilled').sum())),
        refunds=('status', lambda x: int((x == 'refunded').sum())),
        net_gmv_rub=('net_gmv_rub', 'sum'), marketplace_revenue_rub=('marketplace_revenue_rub','sum'),
        variable_cost_rub=('variable_cost_rub','sum'), contribution_90d_rub=('contribution_rub','sum')
    )
    res = (base.merge(marketing,on='channel', validate='one_to_one')
           .merge(rolled.reset_index(),on='channel', how='left')
           .merge(buyers.reset_index(),on='channel',how='left'))
    res = res.fillna(0)
    res['purchase_conversion'] = res['buyers'] / res['acquired_users']
    res['refund_rate'] = res['refunds'] / res['orders']
    res['cac_rub'] = res['marketing_spend_rub'] / res['acquired_users']
    res['ltv90_contribution_rub'] = res['contribution_90d_rub'] / res['acquired_users']
    res['ltv90_to_cac'] = res['ltv90_contribution_rub'] / res['cac_rub']
    res['net_after_marketing_90d_rub'] = res['contribution_90d_rub'] - res['marketing_spend_rub']
    res['contribution_margin'] = res['contribution_90d_rub'] / res['marketplace_revenue_rub']
    res = res.sort_values('channel').reset_index(drop=True)
    return events, res


def verify(users, events, result):
    assert len(users) == 6600
    assert int(result['acquired_users'].sum()) == len(users)
    assert result['fulfilled_orders'].sum() + result['refunds'].sum() == len(events)
    assert np.isclose(result['contribution_90d_rub'].sum(), events['contribution_rub'].sum())
    assert np.isclose(result['net_after_marketing_90d_rub'].sum(), result['contribution_90d_rub'].sum()-result['marketing_spend_rub'].sum())


def main():
    users = pd.read_csv(DATA/'users_synthetic.csv')
    orders = pd.read_csv(DATA/'orders_synthetic.csv')
    marketing = pd.read_csv(DATA/'marketing_synthetic.csv')
    events, result = calculate(users,orders,marketing)
    verify(users,events,result)
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    result.to_csv(OUT/'channel_economics.csv',index=False)
    summary = {
        'disclaimer': 'SYNTHETIC DATA; NOT REAL COMMERCIAL IMPACT',
        'observation_window_days':90,
        'acquired_users':int(result['acquired_users'].sum()),
        'orders':int(result['orders'].sum()),
        'marketing_spend_rub':round(float(result['marketing_spend_rub'].sum()),2),
        'contribution_90d_rub':round(float(result['contribution_90d_rub'].sum()),2),
        'net_after_marketing_90d_rub':round(float(result['net_after_marketing_90d_rub'].sum()),2),
        'channels':{row['channel']:{
            'cac_rub':round(float(row['cac_rub']),2),
            'ltv90_contribution_rub':round(float(row['ltv90_contribution_rub']),2),
            'ltv90_to_cac':round(float(row['ltv90_to_cac']),3),
            'net_after_marketing_90d_rub':round(float(row['net_after_marketing_90d_rub']),2)
        } for _,row in result.iterrows()}
    }
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    plt.figure(figsize=(9,4.5))
    plt.bar(result['channel'],result['ltv90_contribution_rub'],label='90-day contribution per user')
    plt.plot(result['channel'],result['cac_rub'],'o-',label='CAC')
    plt.ylabel('RUB per acquired user')
    plt.title('90-day contribution vs acquisition cost (synthetic)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG/'ltv90_vs_cac.png',dpi=145)
    plt.close()
    plt.figure(figsize=(9,4.5))
    plt.bar(result['channel'],result['net_after_marketing_90d_rub']/1000)
    plt.axhline(0,color='black',linewidth=.7)
    plt.ylabel('Thousands of RUB')
    plt.title('90-day contribution after marketing by channel (synthetic)')
    plt.tight_layout()
    plt.savefig(FIG/'channel_profitability.png',dpi=145)
    plt.close()
    print(result[['channel','acquired_users','cac_rub','ltv90_contribution_rub','ltv90_to_cac','net_after_marketing_90d_rub']].to_string(index=False))
    print('Saved metrics and charts.')

if __name__ == '__main__':
    main()
