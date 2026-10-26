import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
S=L('Sc'); S['d']=S.started_at_pl.dt.normalize()
S['logged0']=S.user_id.notna()&(S.account_completed==0)  # already logged in
x=S[S.slot_selected==1].copy()
x['grp']=np.select([ (x.os=='iOS')&(x.browser=='Safari'), x.os=='iOS', x.device=='tablet'],['iOS-Safari','iOS-other','tablet'],'rest')
x['win']=pd.cut(x.d,pd.to_datetime(['2024-09-30','2026-02-17','2026-03-17','2026-04-17','2026-07-09','2026-10-01']),labels=['<17.02','17.02-16.03','17.03-16.04','17.04-08.07','>=09.07'],right=False)
print(x.pivot_table(index=['grp'],columns='win',values='account_completed',aggfunc='mean',observed=True).round(3).to_string())
print(x.pivot_table(index=['grp','ch'],columns='win',values='account_completed',aggfunc='mean',observed=True).round(3).loc[['iOS-Safari','rest']].to_string())
# daily around 17.03 iOS Safari
y=x[(x.grp=='iOS-Safari')&(x.d.between('2026-03-05','2026-03-29'))].groupby('d').account_completed.agg(['mean','size']); print(y.round(3).to_string())
# tablet by os
t=x[x.device=='tablet']; print(t.pivot_table(index='os',columns='win',values='account_completed',aggfunc='mean',observed=True).round(3).to_string())
print(t.pivot_table(index='os',columns='win',values='account_completed',aggfunc='size',observed=True).to_string())
# is it in account step only? payment_started|account for iOS Safari
z=S[(S.account_completed==1)&(S.os=='iOS')&(S.browser=='Safari')]; print(z.groupby(z.d>= '2026-03-17').payment_started.mean())
