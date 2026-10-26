import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
S,o,U=L('Sc'),L('o'),L('U'); S['d']=S.started_at_pl.dt.normalize()
S['pre_logged']=S.user_id.notna()&(S.account_completed==0)
print(pd.crosstab(S.pre_logged,S.service_selected.astype(int)))
print(S[S.pre_logged].groupby('ch').size().sort_values().tail().to_string(), S[S.pre_logged].landing_page.value_counts().head().to_string())
# returning purchasers: sessions of known users after their first order
S['fo']=S.uid.map(U.coh)
S['returning']=S.uid.notna()&(S.d>S.fo)
w=S.groupby(S.d.dt.to_period('W').dt.start_time).agg(sess=('session_id','size'),ret=('returning','mean'),prelog=('pre_logged','mean'),logged=('user_id',lambda x:x.notna().mean()))
print(w.loc['2025-08-25':'2025-11-10'].round(3).to_string())
# by channel around Sept 29 2025: email/sms traffic?
c=S[S.d.between('2025-09-01','2025-10-31')].groupby([S.d.dt.to_period('W').dt.start_time,'ch']).size().unstack(fill_value=0); print(c.to_string())
