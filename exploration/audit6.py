import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev,users,orders,go,sp=[L(n) for n in 'ses ev users orders go sp'.split()]
qa=orders[orders.promo_code=='TEST-QA'].user_id.unique()
o=pd.read_pickle('o_clean_tmp.pkl'); o=o[~o.user_id.isin(qa)]
print('### GO',len(go),'dup',go.duplicated().sum(),'uniq mid',go.membership_id.nunique(),'orphan user',(~go.user_id.isin(users.user_id)).sum())
print('amount',go.amount_paid.value_counts().to_string()); print('order_id null',go.order_id.isna().sum(),'order not in orders',(go.order_id.notna()&~go.order_id.isin(orders.order_id)).sum())
vu=(pd.to_datetime(go.valid_until)-go.purchased_at.dt.normalize()).dt.days; print('validity days',vu.value_counts().head().to_string())
print('users with >1 GO',go.user_id.value_counts().gt(1).sum())
g=go.sort_values('purchased_at'); g['prev_valid']=g.groupby('user_id').valid_until.shift(); print('bought while active',(pd.to_datetime(g.prev_valid)>=g.purchased_at).sum())
# GO discount validity
m=o[o.discount_type=='go'].merge(go[['user_id','purchased_at','valid_until']],on='user_id',how='left')
m['ok']=(m.purchased_at<=m.created_at)&(pd.to_datetime(m.valid_until)+pd.Timedelta(days=1)>m.created_at)
ok=m.groupby('order_id').ok.any(); print('go-discount orders',len(ok),'without valid membership',(~ok).sum())
bad=o[o.order_id.isin(ok[~ok].index)]; print(bad.created_at.dt.to_period('M').value_counts().sort_index().to_string())
# GO purchase session events
gs=go.session_id; print('GO session in ses',gs.isin(ses.session_id).mean())
# orders vs events
ps=set(ev[ev.event_name=='payment_succeeded'].session_id)
o['has_ps']=o.session_id.isin(ps); print('orders w/o payment_succeeded event',(~o.has_ps).sum()); print(o[~o.has_ps].created_at.dt.to_period('M').value_counts().sort_index().to_string())
pss=ev[ev.event_name=='payment_succeeded'].session_id; print('ps sessions without order or GO', (~pss.isin(o.session_id)&~pss.isin(go.session_id)&~pss.isin(orders.session_id)).sum())
# order time vs session/event time (tz)
x=o.merge(ev[ev.event_name=='payment_succeeded'][['session_id','event_at_utc','event_at_pl']],on='session_id')
d=(x.created_at-x.event_at_pl).dt.total_seconds(); print('created_at - event_pl sec',d.describe().to_string())
x['m']=x.created_at.dt.to_period('M'); print(x.assign(d=d).groupby('m').d.median().to_string())
# order user = session user?
y=o.merge(ses[['session_id','user_id','started_at_pl']],on='session_id',suffixes=('','_s')); print('session user null',y.user_id_s.isna().sum(),'mismatch',(y.user_id_s.notna()&(y.user_id_s!=y.user_id)).sum())
