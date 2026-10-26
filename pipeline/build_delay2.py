import pandas as pd, numpy as np, json
L=lambda n: pd.read_pickle(n+'.pkl')
o,U,go=L('o'),L('U'),L('goc')
D0=pd.Timestamp('2024-10-01')
END=pd.Timestamp('2026-09-30')

# Delay group of first visit (internist, odbyta)
fi=o[(o.n==1)&(o.specialization=='internista')&o.started_at.notna()].set_index('user_id')
fi['delay']=(fi.started_at-fi.scheduled_at).dt.total_seconds()/60
fi['dg']=pd.cut(fi.delay,[-999,10,20,999],labels=['<=10','10-20','>20'])
# patients with no internist first visit or non-odbyta
U2=U.copy()
U2['delay_g']=fi.dg.astype(str).reindex(U2.index).fillna('inne/nieodbyta')

# Simple cube: cohd × delay_g → n, rep30, rep60, rep90, net90, mar90
sec=o[o.n==2].set_index('user_id')
U2['d2']=(sec.created_at.reindex(U2.index)-U2.coh).dt.total_seconds()/86400
g=go.assign(cohd_days=(go.purchased_at.dt.normalize()-D0).dt.days, age=(go.purchased_at.dt.normalize()-go.coh).dt.days)
a90 =o[o.age<=90].groupby('user_id')[['net','margin']].sum()
ga90=g[g.age<=90].groupby('user_id').amount_paid.sum()
a90['net']+=ga90.reindex(a90.index).fillna(0); a90['mar']=a90.margin+ga90.reindex(a90.index).fillna(0)

U2['net90']=a90.net.reindex(U2.index).fillna(0)
U2['mar90']=a90.mar.reindex(U2.index).fillna(0)
U2['cohd']=(U2.coh-D0).dt.days.astype(int)

rows=[]
for (cohd,dg),g2 in U2.groupby(['cohd','delay_g'],observed=True):
    n=len(g2)
    r30=(g2.d2<=30).sum(); r60=(g2.d2<=60).sum(); r90=(g2.d2<=90).sum()
    net90_sum=g2.net90.sum(); mar90_sum=g2.mar90.sum()
    # only rows with enough for chart
    rows.append((int(cohd),str(dg),n,int(r30),int(r60),int(r90),round(float(net90_sum),2),round(float(mar90_sum),2)))

DL2=pd.DataFrame(rows,columns=['cohd','delay_g','n','r30','r60','r90','net90','mar90'])
print('DL2',len(DL2),DL2.delay_g.value_counts().to_dict())

# Read existing, add DL2
data=json.loads(open('data.json').read())
def enc(df):
    out={}
    for c in df.columns:
        if df[c].dtype==object:
            vals=sorted(df[c].astype(str).unique()); m={v:i for i,v in enumerate(vals)}
            out[c]={'dict':vals,'idx':df[c].astype(str).map(m).tolist()}
        else: out[c]=df[c].tolist()
    return out
data['DL2']=enc(DL2)

js=json.dumps(data,separators=(',',':'))
open('data.json','w').write(js)
print('json MB',len(js)/1e6)

# control totals for DL2
print('n sum',DL2.n.sum(),'vs U',len(U))
