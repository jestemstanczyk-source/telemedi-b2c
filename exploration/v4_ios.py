import pandas as pd, numpy as np
S,o=pd.read_pickle('Sc.pkl'),pd.read_pickle('o.pkl')
fot=o[o.n==1].set_index('user_id').created_at
S['typ']=np.where(S.uid.map(fot)<S.started_at_pl,'powracający','nowy')   # powracający = miał opłacone zamówienie przed startem sesji
T=pd.Timestamp('2026-03-17')
S['okno']=np.select([S.started_at_pl.between(T-pd.Timedelta(days=60),T,inclusive='left'),S.started_at_pl.between(T,T+pd.Timedelta(days=60),inclusive='left')],['przed','po'],None)
x=S[(S.os=='iOS')&(S.slot_selected==1)&S.okno.notna()]
def z(a,na,b,nb):
    p=(a+b)/(na+nb); se=np.sqrt(p*(1-p)*(1/na+1/nb)); return (b/nb-a/na)/se
rows=[]
for (typ,br),g in x.groupby(['typ','browser']):
    a=g[g.okno=='przed']; b=g[g.okno=='po']
    if len(a)<20 or len(b)<20: rows.append((typ,br,len(a),len(b),None,None,None,None)); continue
    rows.append((typ,br,len(a),len(b),a.account_completed.mean(),b.account_completed.mean(),(b.account_completed.mean()-a.account_completed.mean())*100,z(a.account_completed.sum(),len(a),b.account_completed.sum(),len(b))))
R=pd.DataFrame(rows,columns=['typ','przeglądarka','n_przed','n_po','przed','po','zmiana_pp','z']); print(R.round(3).to_string(index=False))
# kontrola: Android i desktop w tych samych oknach
y=S[(S.os!='iOS')&(S.slot_selected==1)&S.okno.notna()&(S.typ=='nowy')]
print(y.groupby(['os','okno']).account_completed.agg(['mean','size']).unstack().round(3).to_string())
