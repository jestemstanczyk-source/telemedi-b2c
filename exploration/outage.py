import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
S,o=L('Sc'),L('o'); S['d']=S.started_at_pl.dt.normalize()
g=S.groupby('d')[['payment_started','payment_succeeded','account_completed','slot_selected','service_selected']].sum()
g['ps_rate']=g.payment_succeeded/g.payment_started
med=g.ps_rate.rolling(29,center=True,min_periods=10).median()
print(g[g.ps_rate<med-0.08][['payment_started','payment_succeeded','ps_rate']].round(3).to_string())
print('ps rate dist',g.ps_rate.describe().round(3).to_dict())
# hourly payment success for low days
S['h']=S.started_at_pl.dt.floor('h')
h=S.groupby('h')[['payment_started','payment_succeeded']].sum(); h=h[h.payment_started>=5]; h['r']=h.payment_succeeded/h.payment_started
print('hours with <50% success'); print(h[h.r<0.5].to_string())
# payment method share daily
pm=o.groupby([o.created_at.dt.normalize(),'payment_method']).size().unstack(fill_value=0); pm=pm.div(pm.sum(1),axis=0)
r=pm.rolling(7,center=True).mean(); print(r.resample('MS').mean().round(3).to_string())
low=pm[(pm.blik<0.2)]; print('days blik<20%',low.round(2).to_string())
