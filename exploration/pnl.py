import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
o,U,go,sp,orders=L('o'),L('U'),L('goc'),L('sp'),L('orders')
per=lambda t: np.where(t<'2025-10-01','P','L')
o['p']=per(o.created_at); go['p']=per(go.purchased_at); sp['p']=per(sp.date); U['p']=U.per
R=pd.DataFrame({
 'orders':o.groupby('p').size(),
 'rev_gross_orders':o.groupby('p').amount_paid.sum(),
 'refunds':o.groupby('p').refund_amount.sum(),
 'go_rev':go.groupby('p').amount_paid.sum(),
 'doctor_cost':o.groupby('p').doc_cost.sum(),
 'paid_media':sp.groupby('p').spend_pln.sum(),
 'affiliate':U[U.ch=='rankinglekarzy/affiliate'].groupby('p').size()*25,
 'new_patients':U.groupby('p').size(),
 'promo_discount':o[o.discount_type=='promo'].assign(d=lambda x:x.list_price-x.amount_paid).groupby('p').d.sum(),
 'go_discount':o[o.discount_type=='go'].assign(d=lambda x:x.list_price-x.amount_paid).groupby('p').d.sum(),
}).loc[['P','L']]
R['net_rev']=R.rev_gross_orders-R.refunds+R.go_rev
R['gross_margin']=R.net_rev-R.doctor_cost
R['contribution']=R.gross_margin-R.paid_media-R.affiliate
R['contrib_per_order']=R.contribution/R.orders
R=R.T; R['growth%']=(R.L/R.P-1)*100; print(R.round(1).to_string())
# active patients & orders per patient; GO
act=o.groupby('p').user_id.nunique(); print('active patients',act.to_dict())
# GO standalone vs at checkout; renewal
go['standalone']=go.order_id.isna(); print(pd.crosstab(go.p,go.standalone))
print(pd.crosstab(go.purchased_at.dt.to_period('M'),go.standalone).loc['2025-07':'2025-12'].to_string())
gg=go.sort_values('purchased_at'); gg['nth']=gg.groupby('user_id').cumcount()+1
exp=gg[pd.to_datetime(gg.valid_until)<='2026-08-31']; ren=gg[gg.nth>=2]
nxt=gg.groupby('user_id').purchased_at.shift(-1); gg['renew60']=(nxt-pd.to_datetime(gg.valid_until)).dt.days.le(60)
e=gg[pd.to_datetime(gg.valid_until)<='2026-07-31']; print('expired memberships',len(e),'renewed within 60d of expiry',e.renew60.mean().round(3), 'any repurchase', nxt[e.index].notna().mean().round(3))
