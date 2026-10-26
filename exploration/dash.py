import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
orders,go=L('orders'),L('go')
def per(t): return np.where(t<'2025-10-01','P','L')
def metr(o,g,label):
    o=o.copy(); o['p']=per(o.created_at)
    fo=o.groupby('user_id').created_at.min(); np_=pd.Series(per(fo)).value_counts()
    r=pd.DataFrame({'new_pat':np_,'orders':o.p.value_counts(),'rev_gross':o.groupby('p').amount_paid.sum(),
       'rev_net':o.assign(n=o.amount_paid-o.refund_amount).groupby('p').n.sum(),
       'go':pd.Series(per(g.purchased_at)).value_counts()})
    r=r.loc[['P','L']]; r.loc['growth%']=(r.loc['L']/r.loc['P']-1)*100
    print(label); print(r.round(1).to_string()); print()
metr(orders,go,'RAW (as dashboard?)')
qa=set(orders[orders.promo_code=='TEST-QA'].user_id)
metr(orders.drop_duplicates(),go,'dedup')
o=orders.drop_duplicates(); o=o[~o.user_id.isin(qa)]
metr(o,go[~go.user_id.isin(qa)],'dedup + no QA')
