import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
o,U,go=L('o'),L('U'),L('goc')
o['margin']=o.net-o.doc_cost; o['ch']=o.user_id.map(U.ch); o['camp']=o.user_id.map(U.campaign)
Lp=o[o.created_at>='2025-10-01']
print('margin per held visit by spec x discount (L)'); h=Lp[Lp.status.isin(['completed','refunded'])]
print(h.pivot_table(index='specialization',columns='discount_type',values='margin',aggfunc=['mean','size']).round(1).to_string())
gs=Lp[(Lp.discount_type=='go')&(Lp.specialization!='internista')]; print('GO specialist orders L',len(gs),'total margin',gs.margin.sum().round(), 'negative margin orders',(gs.margin<0).sum(), 'sum of negatives',gs.margin[gs.margin<0].sum().round())
# social L4 refunds in L
s=Lp[Lp.ch.isin(['meta/paid_social','tiktok/paid_social'])&(Lp.visit_purpose=='l4')]
print('social L4 orders L',len(s),'refunded',(s.status=='refunded').mean().round(3),'refund zl',s.refund_amount[s.status=='refunded'].sum(),'doc cost on refunded',s.doc_cost[s.status=='refunded'].sum())
ex=len(s)*(s.status=='refunded').mean()-len(s)*0.055; print('excess refunds vs 5.5%',round(ex), 'value', round(ex*(s[s.status=='refunded'].amount_paid.mean()+25)))
# promo cost L4SZYBKO20 & TIKTOK25 in L
print(Lp[Lp.discount_type=='promo'].groupby('promo_code').agg(n=('order_id','size'),disc=('list_price',lambda x: 0)).to_string())
pr=Lp[Lp.discount_type=='promo']; print((pr.list_price-pr.amount_paid).groupby(pr.promo_code).sum().to_string())
# GO members: margin 365 vs non-GO among internist-first patients, same channel (correlational)
end=pd.Timestamp('2026-09-30'); M=U[U.coh<=end-pd.Timedelta(days=365)].copy()
oa=o[o.age<=365].groupby('user_id').agg(ord=('order_id','size'),mar=('margin','sum')); M=M.join(oa)
gm=go.assign(age=(go.purchased_at.dt.normalize()-go.coh).dt.days); gm=gm[gm.age<=365].groupby('user_id').amount_paid.sum()
M['go']=M.index.isin(gm.index); M['mar']+=gm.reindex(M.index).fillna(0)
print(M.groupby(['f_specialization','go'])[['ord','mar']].mean().loc[['internista']].round(2).to_string(), M.groupby('go').size().to_string())
# GO expiring per year ahead
print('GO valid_until in next 12 months', go[(pd.to_datetime(go.valid_until)>'2026-09-30')].shape[0])
