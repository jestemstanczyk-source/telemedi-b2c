import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev,users,orders,go,sp=[L(n) for n in 'ses ev users orders go sp'.split()]
ses['d']=ses.started_at_pl.dt.normalize()
ses['ch']=ses.utm_source.fillna('direct')+'/'+ses.utm_medium.fillna('none')
dd=ses.groupby(['d','ch']).size().unstack(fill_value=0)
tot=dd.sum(1)
# robust anomaly: ratio to rolling median 15d
r=tot/tot.rolling(15,center=True,min_periods=5).median()
print('total anomalies'); print(r[(r<0.6)|(r>1.6)].round(2).to_string())
for c in dd.columns:
    s=dd[c]; rr=s/s.rolling(15,center=True,min_periods=5).median().replace(0,np.nan)
    a=rr[(rr<0.4)|(rr>2.5)]
    if len(a): print(c, len(a), [(str(k.date()),round(v,2)) for k,v in a.head(25).items()])
# zero days per channel within active span
for c in dd.columns:
    s=dd[c]; z=s[(s==0)]; print(c,'zero days',len(z), [str(k.date()) for k in z.index[:15]])
# clicks vs sessions per campaign
sc=ses.groupby([ses.d.rename('date'),'utm_campaign']).size().rename('sess')
m=sp.set_index(['date','utm_campaign']).join(sc).fillna({'sess':0})
m['ratio']=m.sess/m.clicks
mm=m.groupby([pd.Grouper(level='date',freq='MS'),'utm_campaign']).apply(lambda g:g.sess.sum()/g.clicks.sum()).unstack().round(2); print(mm.to_string())
