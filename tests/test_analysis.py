import sys
from pathlib import Path
import pandas as pd
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.generate_data import generate
from src.analysis import calculate, verify, enrich_orders

def test_reproducibility():
    a=generate(); b=generate()
    for x,y in zip(a,b): pd.testing.assert_frame_equal(x,y)

def test_economic_identity():
    u,o,m=generate()
    ev,summary=calculate(u,o,m)
    verify(u,ev,summary)
    assert np.isclose(summary['ltv90_to_cac'],summary['contribution_90d_rub']/summary['marketing_spend_rub']).all()

def test_refund_only_handling_cost():
    users=pd.DataFrame([{'user_id':1,'channel':'X','acquired_at':'2026-01-01'}])
    orders=pd.DataFrame([{'order_id':1,'user_id':1,'ordered_at':'2026-01-02','gmv_rub':1000.,'status':'refunded'}])
    ev=enrich_orders(users,orders)
    assert ev.loc[0,'contribution_rub']==-45
    assert ev.loc[0,'net_gmv_rub']==0

def test_fulfilled_order_contribution():
    users=pd.DataFrame([{'user_id':1,'channel':'X','acquired_at':'2026-01-01'}])
    orders=pd.DataFrame([{'order_id':1,'user_id':1,'ordered_at':'2026-01-02','gmv_rub':1000.,'status':'fulfilled'}])
    ev=enrich_orders(users,orders)
    assert np.isclose(ev.loc[0,'contribution_rub'], 150+35-22-65-12)
