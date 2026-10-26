import pandas as pd, numpy as np
o,U=pd.read_pickle('o.pkl'),pd.read_pickle('U.pkl')
END=pd.Timestamp('2026-09-30')
f=o[o.n==1].set_index('user_id')
f=f[(f.specialization=='internista')&f.started_at.notna()].copy()   # pierwsza wizyta u internisty, odbyta
f['delay']=(f.started_at-f.scheduled_at).dt.total_seconds()/60
f=f[f.created_at.dt.normalize()<=END-pd.Timedelta(days=60)]          # pełne 60 dni obserwacji
f['g']=np.select([f.delay<=10,f.delay>20],['<=10','>20'],'10-20')
sec=o[o.n==2].set_index('user_id').created_at
f['ret60']=((sec.reindex(f.index)-f.created_at).dt.total_seconds()<=60*86400)
f['ch']=U.ch.reindex(f.index)
f['core']=f.ch.map(lambda c:'google' if c.startswith('google') else 'direct' if c=='direct/none' else 'polecenia' if c=='polecenie/referral' else None)
f['l4']=np.where(f.visit_purpose=='l4','L4','reszta')
def tab(df,by):
    t=df[df.g!='10-20'].groupby(by+['g']).ret60.agg(['mean','size']).unstack('g'); t['diff_pp']=(t[('mean','>20')]-t[('mean','<=10')])*100; return t.round(3)
print('Wszyscy'); print(tab(f.assign(all='all'),['all']).to_string())
c=f[f.core.notna()]
print('\nKanały podstawowe'); print(tab(c,['core']).to_string()); print(tab(c.assign(all='razem'),['all']).to_string())
print('\nCel wizyty (kanały podstawowe)'); print(tab(c,['l4']).to_string())
print('\nKanał x cel'); print(tab(c,['core','l4']).to_string())
# standaryzacja: ważona różnica w warstwach cel (MH-like, wagi = liczebność >20)
s=c[c.g!='10-20'].groupby(['l4','g']).ret60.agg(['mean','size']).unstack('g')
w=s[('size','>20')]; d=(s[('mean','>20')]-s[('mean','<=10')]); print('\nRóżnica po kontroli celu (ważona liczebnością >20): %.1f pp'%(100*(d*w).sum()/w.sum()))
print('Udział L4: <=10',(c[c.g=='<=10'].l4=='L4').mean().round(3),' >20',(c[c.g=='>20'].l4=='L4').mean().round(3))
# kontrola dodatkowo: tylko kohorty od 2025-12 (kiedy opóźnienia częste)
cc=c[c.created_at>='2025-12-01']; print('\nTylko kohorty od XII 2025'); print(tab(cc,['l4']).to_string())
# logit
# kontrola pory: tylko wizyty 6-11, okres od XII 2025, w warstwach cel x kanał
h=c.scheduled_at.dt.hour; mc=c[(h.between(6,11))&(c.created_at>='2025-12-01')]
s=mc[mc.g!='10-20'].groupby(['core','l4','g']).ret60.agg(['mean','size']).unstack('g').dropna()
w=s[('size','>20')]; d=s[('mean','>20')]-s[('mean','<=10')]
print('\nRano 6-11, kohorty od XII 2025, warstwy kanał x cel:'); print(s.round(3).to_string()); print('Różnica ważona: %.1f pp (n>20=%d)'%(100*(d*w).sum()/w.sum(),w.sum()))
