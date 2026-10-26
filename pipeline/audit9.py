import pandas as pd, numpy as np
pd.set_option('display.width',250)
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev=L('ses'),L('ev')
ses['w']=ses.started_at_pl.dt.to_period('W').dt.start_time
ses['ch']=ses.utm_source.fillna('direct')+'/'+ses.utm_medium.fillna('none')
w=ev.assign(v=1).pivot_table(index='session_id',columns='event_name',values='v',aggfunc='max')
S=ses.join(w,on='session_id').fillna({c:0 for c in w.columns})
steps=['service_selected','slot_selected','account_completed','payment_started','payment_succeeded']
g=S.groupby('w')
out=pd.DataFrame({'sess':g.size(),'logged':g.user_id.apply(lambda x:x.notna().mean()),'direct':g.ch.apply(lambda x:(x=='direct/none').mean()),'mobile':g.device.apply(lambda x:(x=='mobile').mean()),'inapp':g.browser.apply(lambda x:x.isin(['Instagram','Facebook','TikTok']).mean())})
prev='sess'
for s in steps: out[s[:6]]=g[s].sum()/ (g.size() if prev=='sess' else g[prev].sum()); prev=s
out['conv']=g.payment_succeeded.mean()
print(out.round(3).to_string())
S.to_pickle('S.pkl')
