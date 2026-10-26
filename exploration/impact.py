import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
S,o=L('Sc'),L('o'); S['d']=S.started_at_pl.dt.normalize()
x=S[(S.os=='iOS')&(S.browser=='Safari')&(S.slot_selected==1)&(S.user_id.isna()|(S.account_completed==1))]
pre=x[x.d.between('2026-01-15','2026-03-16')]; post=x[x.d>='2026-03-17']
a0,a1=pre.account_completed.mean(),post.account_completed.mean()
down=post[post.account_completed==1].payment_succeeded.mean()
days=post.d.nunique(); slots=len(post)/days
lost=slots*(a0-a1)*down
aov=o[o.created_at>='2026-03-17'].assign(m=lambda d:d.net-d.doc_cost).m.mean()
print(f'acct rate {a0:.3f}->{a1:.3f}, slot sess/day {slots:.1f}, downstream {down:.3f}, lost orders/day {lost:.1f}, days {days}, total {lost*days:.0f}, margin/order {aov:.1f}, lost margin {lost*days*aov:.0f}, per year {lost*365*aov:.0f}')
# social funnel inapp vs not
soc=S[S.ch.isin(['meta/paid_social','tiktok/paid_social'])].copy(); soc['inapp']=soc.browser.isin(['Instagram','Facebook','TikTok'])
st=['service_selected','slot_selected','account_completed','payment_started','payment_succeeded']
f=soc.groupby(['utm_campaign','inapp'])[st].sum(); f.insert(0,'sess',soc.groupby(['utm_campaign','inapp']).size())
r=f.copy(); 
for i in range(1,len(r.columns)): r.iloc[:,i]=f.iloc[:,i]/f.iloc[:,i-1]
r['conv']=f.payment_succeeded/f.sess; print(r.round(3).to_string())
# all traffic inapp vs not, excluding social
