import pandas as pd, numpy as np
pd.set_option('display.width',250)
L=lambda n: pd.read_pickle(n+'.pkl')
o,U,go=L('o'),L('U'),L('goc')
end=pd.Timestamp('2026-09-30'); H=90
M=U[U.coh<=end-pd.Timedelta(days=H)].copy(); M['r']=M.d2<=H
a=o[o.age<=H].groupby('user_id')[['net','margin']].sum(); M=M.join(a)
g=go.assign(age=(go.purchased_at.dt.normalize()-go.coh).dt.days); g=g[g.age<=H].groupby('user_id').amount_paid.sum(); M['net']+=g.reindex(M.index).fillna(0); M['margin']+=g.reindex(M.index).fillna(0)
t=M.groupby(['ch','per']).agg(n=('r','size'),rep90=('r','mean'),net90=('net','mean'),mar90=('margin','mean')).unstack('per'); print(t.round(3).to_string())
# mix decomposition of rep90 P->L
for k in ['r','margin']:
    gp=M.groupby(['per','ch'])[k].mean().unstack(0); w=M.groupby(['per','ch']).size().unstack(0); w=w/w.sum()
    tot={p:(gp[p]*w[p]).sum() for p in ['P','L']}
    mixfx=((w.L-w.P)*gp.P).sum(); behfx=(w.L*(gp.L-gp.P).fillna(0)).sum()
    print(k,'P',round(tot['P'],3),'L',round(tot['L'],3),'mix effect',round(mixfx,3),'within-channel',round(behfx,3), '(tiktok only in L; its rate counted in mix)')
# within paid social, inapp vs not; first-order purpose by channel
print(M.groupby(['ch','f_visit_purpose']).r.mean().unstack().round(3).to_string())
print(pd.crosstab(U.ch,U.f_visit_purpose,normalize='index').round(2).to_string())
print(pd.crosstab([U.ch,U.per],U.f_promo_code,normalize='index').round(2).to_string())
