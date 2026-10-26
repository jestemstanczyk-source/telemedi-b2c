import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev,users,orders,go,sp=[L(n) for n in 'ses ev users orders go sp'.split()]
o=orders.drop_duplicates().copy()
q=o[o.user_id.isin(o[o.promo_code=='TEST-QA'].user_id)&(o.promo_code!='TEST-QA')]
print('QA users other orders'); print(q[['amount_paid','discount_type','status','specialization']].describe(include='all').to_string()); print(ses[ses.session_id.isin(q.session_id)].landing_page.value_counts().head().to_string())
o=o[o.promo_code!='TEST-QA']
o['disc']=o.list_price-o.amount_paid
print('\namount vs discount');print(o.groupby(['discount_type','specialization']).apply(lambda g: g.amount_paid.div(g.list_price).round(3).value_counts().head(4).to_dict(),include_groups=False).to_string())
print(o.groupby('promo_code').disc.agg(['mean','min','max','count']).to_string())
print('\nstatus x refund'); o['rf']=np.select([o.refund_amount==0,np.isclose(o.refund_amount,o.amount_paid),o.refund_amount>o.amount_paid],['zero','full','over'],'partial')
print(pd.crosstab(o.status,o.rf).to_string())
print('\nstatus x started_at null'); print(pd.crosstab(o.status,o.started_at.isna()).to_string())
print(pd.crosstab(o.status,o.duration_min.isna()).to_string())
print('rating by status'); print(o.groupby('status').rating.agg(['count','mean']).to_string())
lag=(o.scheduled_at-o.created_at).dt.total_seconds()/60; print('sched-created min',lag.describe().to_string()); print('sched before created',(lag<0).sum())
st=(o.started_at-o.scheduled_at).dt.total_seconds()/60; print('start-sched',st.describe().to_string())
print('duration',o.duration_min.describe().to_string())
print('amount_paid<=0',(o.amount_paid<=0).sum(),'>list',(o.amount_paid>o.list_price+0.01).sum())
o.to_pickle('o_clean_tmp.pkl')
