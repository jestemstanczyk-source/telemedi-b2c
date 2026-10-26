import pandas as pd, numpy as np, json
o=pd.read_pickle('o.pkl')
D0=pd.Timestamp('2024-10-01')

# --- delay cube (internist only, visits with started_at)
x=o[(o.specialization=='internista')&o.started_at.notna()].copy()
x['delay']=(x.started_at-x.scheduled_at).dt.total_seconds()/60
x['h']=x.scheduled_at.dt.hour
x['slot']=np.select([x.h.between(6,11),x.h.between(12,17),x.h.between(18,23)],['06-11','12-17','18-23'],'00-05')
x['late20']=(x.delay>20).astype(int)
x['late10']=(x.delay>10).astype(int)
x['rated']=(x.rating>0).astype(int)
x['rating_v']=x.rating.fillna(0)
x['rating_w']=x.rating.notna().astype(int)
x['d']=(x.scheduled_at.dt.normalize()-D0).dt.days.astype(int)

# cube: d × slot
g=x.groupby(['d','slot']).agg(
    n=('delay','size'),
    late20=('late20','sum'),
    late10=('late10','sum'),
    delay_sum=('delay','sum'),
    rating_sum=('rating_v','sum'),
    rating_n=('rating_w','sum')
).reset_index()
g['slot_idx']=pd.Categorical(g.slot,['00-05','06-11','12-17','18-23']).codes.astype(int)

# by delay bucket (for retention context) — already computed, embed as static
# ≤10, 10-20, >20: ret60 values (from v2_ret.py logic, core channels)
ret_by_delay={'<=10':0.202,'>20':0.081}   # core channels as computed

# iOS cube
S=pd.read_pickle('Sc.pkl')
fot=o[o.n==1].set_index('user_id').created_at
S['typ']=np.where(S.uid.map(fot)<S.started_at_pl,'ret','new')
T=pd.Timestamp('2026-03-17')
S['d']=(S.started_at_pl.dt.normalize()-D0).dt.days.astype(int)
ios=S[(S.os=='iOS')&(S.slot_selected==1)].copy()
ib=pd.Categorical(ios.browser,['Safari','Chrome','Facebook','Instagram','TikTok','Firefox'])
ios['br']=ib.codes.astype(int)
ios['br_valid']=(ib.codes>=0).astype(int)
ios2=ios[ios.br_valid==1].copy()
ig=ios2.groupby(['d','br','typ']).agg(
    slot=('slot_selected','size'),
    acc=('account_completed','sum')
).reset_index()
# typ → 0=new, 1=ret
ig['typ_idx']=(ig.typ=='ret').astype(int)

print('delay rows',len(g),'ios rows',len(ig))
print('d range',g.d.min(),g.d.max(), 'ios d',ig.d.min(),ig.d.max())
print('slots',g.slot.unique(),'ios browsers',['Safari','Chrome','Facebook','Instagram','TikTok','Firefox'])

def enc(df):
    out={}
    for c in df.columns:
        if df[c].dtype==object:
            vals=sorted(df[c].astype(str).unique()); m={v:i for i,v in enumerate(vals)}
            out[c]={'dict':vals,'idx':df[c].astype(str).map(m).tolist()}
        else: out[c]=df[c].tolist()
    return out

# embed alongside existing data.json by reading and extending
existing=json.loads(open('data.json').read())
existing['DL']=enc(g)  # delay cube
existing['IOS']=enc(ig)  # iOS cube
existing['IOS_BR']=['Safari','Chrome','Facebook','Instagram','TikTok','Firefox']
existing['IOS_TYP']=['nowy','powracający']
existing['SLOTS']=['00-05','06-11','12-17','18-23']
existing['ret_by_delay']=ret_by_delay

js=json.dumps(existing,separators=(',',':'))
open('data.json','w').write(js)
print('new json MB',len(js)/1e6)
