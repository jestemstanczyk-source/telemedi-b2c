import pandas as pd, numpy as np
users,o,S,go,orders=[pd.read_pickle(f+'.pkl') for f in ['users','o','Sc','goc','orders']]
qa=set(orders[orders.promo_code=='TEST-QA'].user_id); u=users[~users.user_id.isin(qa)].set_index('user_id')
fo=o.groupby('user_id').created_at.min(); fgo=go.groupby('user_id').purchased_at.min()
u['first_order']=fo; u['first_go']=fgo
u['no_order']=u.first_order.isna(); u['no_pay']=u.first_order.isna()&u.first_go.isna()
print('kont',len(u),' bez opłaconego zamówienia konsultacji',u.no_order.sum(),f'({u.no_order.mean():.1%})',' bez jakiejkolwiek płatności (też GO)',u.no_pay.sum())
u['q']=u.registered_at.dt.to_period('Q')
print(u.groupby('q').agg(konta=('no_order','size'),bez_zam=('no_order','sum'),odsetek=('no_order','mean')).round(3).to_string())
lag=(u.first_order-u.registered_at).dt.total_seconds()
print('\nCzas rejestracja -> 1. zapłata (min):',(lag/60).describe(percentiles=[.5,.9,.99]).round(1).to_dict())
print('ten sam dzień',(lag<86400).mean().round(4),' >1 dzień',(lag>=86400).sum(),' >30 dni',(lag>=30*86400).sum())
print((lag[lag>=86400]/86400).describe().round(1).to_dict())
# sesje e-mail/sms po rejestracji dla kont bez zamówienia (sesje z user_id lub zszyte przez visitor_id)
nz=u[u.no_order].index; s=S[S.uid.isin(nz)].copy(); s['reg']=s.uid.map(u.registered_at)
s=s[s.started_at_pl>s.reg]
em=s[s.utm_medium.isin(['email','sms'])]
print('\nKont bez zamówienia z jakąkolwiek sesją po rejestracji',s.uid.nunique(),' z sesją email/sms',em.uid.nunique(), em.utm_medium.value_counts().to_dict(), em.utm_campaign.value_counts().head().to_dict())
# dla porównania: konta z zamówieniem
yz=u[~u.no_order].index; s2=S[S.uid.isin(yz)&S.utm_medium.isin(['email','sms'])]; print('Kont z zamówieniem, z sesją email/sms',s2.uid.nunique(),'z',len(yz))
# co robiły konta bez zamówienia w sesji rejestracji
r=S[S.uid.isin(nz)&(S.account_completed==1)]; print('\nSesje z account_completed kont bez zamówienia',len(r),' z payment_started',int(r.payment_started.sum()),' z payment_succeeded',int(r.payment_succeeded.sum()))
print('ostatni krok w sesji rejestracji:',r.assign(k=np.select([r.payment_started==1],['payment_started'],'account_completed')).k.value_counts().to_dict())
print('marketing_consent: bez zam',u[u.no_order].marketing_consent.mean().round(3),' z zam',u[~u.no_order].marketing_consent.mean().round(3))
