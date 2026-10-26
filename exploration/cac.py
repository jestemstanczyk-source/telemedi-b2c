import pandas as pd, numpy as np
pd.set_option('display.width',250)
L=lambda n: pd.read_pickle(n+'.pkl')
o,U,go,sp=L('o'),L('U'),L('goc'),L('sp')
end=pd.Timestamp('2026-09-30')
sp['per']=np.where(sp.date<'2025-10-01','P','L')
o['margin']=o.net-o.doc_cost
g=go.assign(age=(go.purchased_at.dt.normalize()-go.coh).dt.days)
def val(h):
    a=o[o.age<=h].groupby('user_id').margin.sum(); b=g[g.age<=h].groupby('user_id').amount_paid.sum(); return a.add(b,fill_value=0)
U['m90']=val(90); U['m180']=val(180); U['mall']=val(10**5)
U['mat90']=U.coh<=end-pd.Timedelta(days=90); U['mat180']=U.coh<=end-pd.Timedelta(days=180)
key='campaign'
s=sp.rename(columns={'utm_campaign':'campaign'}).groupby([key,'per']).spend_pln.sum().unstack()
n=U.groupby([key,'per']).size().unstack()
m90=U[U.mat90].groupby([key,'per']).m90.mean().unstack(); m180=U[U.mat180].groupby([key,'per']).m180.mean().unstack()
T=pd.concat({'spend':s,'new':n,'CAC':s/n,'m90':m90,'m180':m180},axis=1).swaplevel(axis=1).sort_index(axis=1)
print(T.round(1).to_string())
# total paid
for p in ['P','L']:
    tot_sp=sp[sp.per==p].spend_pln.sum(); aff=(U[(U.per==p)&(U.ch=='rankinglekarzy/affiliate')].shape[0])*25
    print(p,'spend',round(tot_sp),'affiliate',aff,'new',(U.per==p).sum(),'blended CAC',round((tot_sp+aff)/(U.per==p).sum(),1))
# monthly spend by source
print(sp.groupby([sp.date.dt.to_period('Q'),'utm_source']).spend_pln.sum().unstack().round(0).to_string())
U.to_pickle('U.pkl')
