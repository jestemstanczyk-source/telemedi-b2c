import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
S,o=L('Sc'),L('o')
S['d']=S.started_at_pl.dt.normalize()
S['inapp']=S.browser.isin(['Instagram','Facebook','TikTok'])
steps=['service_selected','slot_selected','account_completed','payment_started','payment_succeeded']
def best_cp(num,den,minseg=21):
    num=num.values.astype(float); den=den.values.astype(float); n=len(num); best=(0,None,None,None)
    cn=np.cumsum(num); cd=np.cumsum(den)
    for k in range(minseg,n-minseg):
        p1=cn[k-1]/cd[k-1]; p2=(cn[-1]-cn[k-1])/(cd[-1]-cd[k-1]); p=cn[-1]/cd[-1]
        se=np.sqrt(p*(1-p)*(1/cd[k-1]+1/(cd[-1]-cd[k-1])))
        z=(p2-p1)/se if se>0 else 0
        if abs(z)>abs(best[0]): best=(z,k,p1,p2)
    return best
segs={'all':S,'mobile':S[S.device=='mobile'],'desktop':S[S.device=='desktop'],'tablet':S[S.device=='tablet'],
 'inapp':S[S.inapp],'not_inapp':S[~S.inapp],'iOS':S[S.os=='iOS'],'Android':S[S.os=='Android'],'Safari':S[S.browser=='Safari'],'Chrome':S[S.browser=='Chrome'],
 'Instagram':S[S.browser=='Instagram'],'Facebook':S[S.browser=='Facebook'],'google_cpc':S[S.ch=='google/cpc'],'meta':S[S.ch=='meta/paid_social'],'logged_in_start':S[S.user_id.notna()]}
rows=[]
for nm,d in segs.items():
    g=d.groupby('d')[steps].sum(); g['sess']=d.groupby('d').size()
    prev='sess'
    for s in steps:
        z,k,p1,p2=best_cp(g[s],g[prev]); rows.append((nm,f'{prev[:7]}->{s[:7]}',g.index[k].date() if k else None,round(p1,3),round(p2,3),round(z,1))); prev=s
R=pd.DataFrame(rows,columns=['seg','step','cp','before','after','z']); R=R[R.z.abs()>6].sort_values('z',key=abs,ascending=False)
print(R.to_string())
