import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
o,U=L('o'),L('U')
o['ch']=o.user_id.map(U.ch); o['camp']=o.user_id.map(U.campaign)
fo=o[o.n==1]
t=pd.crosstab([fo.ch,fo.per],fo.status,normalize='index').round(3); print(t.to_string())
print(pd.crosstab([fo.visit_purpose],fo.status,normalize='index').round(3).to_string())
print(pd.crosstab([fo.camp],fo.status,normalize='index').round(3).to_string())
# L4 refunded over time all channels
l4=o[o.visit_purpose=='l4']; print(l4.groupby(l4.created_at.dt.to_period('Q')).status.value_counts(normalize=True).unstack().round(3).to_string())
# within L4 & not social: has refund rate changed?
x=fo[(fo.visit_purpose=='l4')]; print(pd.crosstab([x.ch.isin(['meta/paid_social','tiktok/paid_social']),x.per],x.status,normalize='index').round(3).to_string())
# no_show by mode, by channel
print(pd.crosstab([fo.ch],fo.consultation_mode,normalize='index').round(2).to_string())
print(fo.groupby(['ch']).rating.mean().round(2).to_string())
