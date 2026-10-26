import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
S,orders,go,users,sp=L('S'),L('orders'),L('go'),L('users'),L('sp')
qa=set(orders[orders.promo_code=='TEST-QA'].user_id)
o=orders.drop_duplicates(); o=o[~o.user_id.isin(qa)].copy()
go=go[~go.user_id.isin(qa)].copy(); S=S[~S.user_id.isin(qa)]
v2u=S.dropna(subset=['user_id']).groupby('visitor_id').user_id.first()
S['uid']=S.user_id.fillna(S.visitor_id.map(v2u))
S=S[~S.uid.isin(qa)].copy()
S['ch']=S.utm_source.fillna('direct')+'/'+S.utm_medium.fillna('none')
DOC={'internista':25,'psychiatra':200}
held=o.status.isin(['completed','refunded'])
o['doc_cost']=np.where(held,o.specialization.map(DOC).fillna(100),0)
o['net']=o.amount_paid-o.refund_amount
o=o.sort_values('created_at'); o['n']=o.groupby('user_id').cumcount()+1
fo=o[o.n==1].set_index('user_id')
o['coh']=o.user_id.map(fo.created_at.dt.normalize())
o['age']=(o.created_at.dt.normalize()-o.coh).dt.days
# GO revenue per user, attach
go['coh']=go.user_id.map(fo.created_at.dt.normalize())
# attribution first touch
x=S[S.uid.isin(fo.index)].copy(); x['fo_t']=x.uid.map(fo.created_at)
pre=x[x.started_at_pl<=x.fo_t].sort_values('started_at_pl')
ft=pre.groupby('uid').head(1).set_index('uid')
ls=S.set_index('session_id').loc[fo.session_id]
U=pd.DataFrame(index=fo.index)
U['coh']=fo.created_at.dt.normalize()
U['ch']=ft.ch; U['campaign']=ft.utm_campaign.fillna('(none)')
U['device']=ls.device.values; U['browser']=ls.browser.values; U['landing']=ft.landing_page
U['inapp']=U.browser.isin(['Instagram','Facebook','TikTok'])
for c in ['specialization','visit_purpose','consultation_mode','discount_type','promo_code','status','list_price','amount_paid']: U['f_'+c]=fo[c]
U['f_promo_code']=U.f_promo_code.fillna('(none)')
U['go_at_first']=fo.order_id.isin(go.order_id)
U=U.join(users.set_index('user_id')[['region','city_size','gender','birth_year','marketing_consent']])
U['per']=np.where(U.coh<'2025-10-01','P','L')
o.to_pickle('o.pkl'); go.to_pickle('goc.pkl'); U.to_pickle('U.pkl'); S.to_pickle('Sc.pkl')
print(U.shape); print(U.ch.value_counts().to_string()); print(U.isna().sum()[U.isna().sum()>0])
