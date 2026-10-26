import pandas as pd, numpy as np
pd.set_option('display.width',250)
L=lambda n: pd.read_pickle(n+'.pkl')
o,U,go=L('o'),L('U'),L('goc')
o['per']=np.where(o.created_at<'2025-10-01','P','L')
print('NEW PATIENTS by channel'); t=pd.crosstab(U.ch,U.per)[['P','L']]; t['delta']=t.L-t.P; t['g%']=(t.L/t.P-1)*100; t.loc['TOTAL']=t.sum(); t.loc['TOTAL','g%']=(t.loc['TOTAL','L']/t.loc['TOTAL','P']-1)*100; print(t.round(1).to_string())
print('\nORDERS new vs repeat'); o['kind']=np.where(o.n==1,'first','repeat'); t=pd.crosstab(o.kind,o.per)[['P','L']]; t['g%']=(t.L/t.P-1)*100; print(t.round(1).to_string())
# repeat orders by cohort period
o['cper']=np.where(o.coh<'2025-10-01','P','L'); print(pd.crosstab([o.kind,o.cper],o.per).to_string())
# retention at fixed horizon: share of cohort with 2nd order within 30/90/180 days; cohorts must be mature
end=pd.Timestamp('2026-09-30')
sec=o[o.n==2].set_index('user_id').age
U['d2']=sec.reindex(U.index)
U['m']=U.coh.dt.to_period('M')
res=[]
for h in [30,90,180]:
    mat=U[U.coh<=end-pd.Timedelta(days=h)]
    res.append(mat.groupby('m').d2.apply(lambda s:(s<=h).mean()).rename(f'rep{h}'))
# revenue/margin per patient at 90 days
o['margin']=o.net-o.doc_cost
gg=go.copy(); gg['age']=(gg.purchased_at.dt.normalize()-gg.coh).dt.days
def at(h):
    a=o[o.age<=h].groupby('user_id')[['net','margin']].sum()
    g=gg[gg.age<=h].groupby('user_id').amount_paid.sum()
    a['go']=g.reindex(a.index).fillna(0); a['net']+=a.go; a['margin']+=a.go
    return a
a90=at(90); mat=U[U.coh<=end-pd.Timedelta(days=90)].join(a90)
res+= [mat.groupby('m').net.mean().rename('net90'), mat.groupby('m').margin.mean().rename('mar90')]
res.append(U.groupby('m').size().rename('n'))
fo=o[o.n==1]; fo_m=fo.coh.dt.to_period('M')
res.append(fo.groupby(fo_m).status.apply(lambda s:(s!='completed').mean()).rename('bad1st'))
res.append(fo.groupby(fo_m).discount_type.apply(lambda s:(s=='promo').mean()).rename('promo1st'))
res.append(U.groupby('m').go_at_first.mean().rename('go1st'))
R=pd.concat(res,axis=1); print(R.round(3).to_string())
U.to_pickle('U.pkl'); o.to_pickle('o.pkl')
