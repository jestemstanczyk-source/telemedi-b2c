import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
S,orders=L('S'),L('orders')
qa=set(orders[orders.promo_code=='TEST-QA'].user_id)
o=orders.drop_duplicates(); o=o[~o.user_id.isin(qa)]
v2u=S.dropna(subset=['user_id']).groupby('visitor_id').user_id.first()
S['uid']=S.user_id.fillna(S.visitor_id.map(v2u))
print('sessions stitched to a user', S.uid.notna().mean(), ' of which not logged', (S.uid.notna()&S.user_id.isna()).sum())
fo=o.sort_values('created_at').groupby('user_id').first()
x=S[S.uid.isin(fo.index)].merge(fo[['session_id','created_at']].rename(columns={'session_id':'fo_sid','created_at':'fo_t'}),left_on='uid',right_index=True)
pre=x[x.started_at_pl<=x.fo_t]
n=pre.groupby('uid').size(); print('sessions up to first order',n.describe().to_string()); print(n.value_counts().head(8).to_string())
lag=(pre.fo_t-pre.started_at_pl).dt.days; print('lag days of pre sessions',lag.describe().to_string(), (lag>30).mean())
f=pre.sort_values('started_at_pl').groupby('uid').first(); l=pre[pre.session_id==pre.fo_sid].set_index('uid')
f['ch']=f.utm_source.fillna('direct')+'/'+f.utm_medium.fillna('none'); l['ch']=l.utm_source.fillna('direct')+'/'+l.utm_medium.fillna('none')
print(pd.crosstab(f.ch,l.ch.reindex(f.index),margins=True).to_string())
# first order session landing for direct last touch
print('first order session landing', l.landing_page.value_counts().head(8).to_string())
