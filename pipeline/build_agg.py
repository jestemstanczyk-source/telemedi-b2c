import pandas as pd, numpy as np, json
L=lambda n: pd.read_pickle(n+'.pkl')
o,U,go,sp,S=L('o'),L('U'),L('goc'),L('sp'),L('Sc')
D0=pd.Timestamp('2024-10-01')
PAID=['gs_brand','gs_generic_erecepta','gs_generic_l4','gs_generic_lekarz_online','gs_generic_specjalisci','meta_prosp_l4_szybko','meta_prosp_lekarz_online','meta_rmkt_koszyk','tt_prosp_l4_15min']
U['acq']=np.where(U.campaign.isin(PAID),U.campaign,U.ch)
U['disc']=np.where(U.go_at_first,'go_kupione_przy_1',U.f_discount_type)
U['inapp']=U.inapp.map({True:'in-app',False:'przegladarka'})
_f=o[o.n==1].set_index('user_id'); _dl=(_f.started_at-_f.scheduled_at).dt.total_seconds()/60
U['f_delay']=pd.Series(np.select([_dl.isna(),_dl<=10,_dl<=20],['nieodbyta','<=10 min','10-20 min'],'>20 min'),index=_f.index).reindex(U.index)
AGES=[0,7,30,60,90,180,365]
o['margin']=o.net-o.doc_cost
g=go.assign(age=(go.purchased_at.dt.normalize()-go.coh).dt.days)
o['bad']=o.status.isin(['refunded','cancelled']).astype(int); o['ns']=(o.status=='no_show').astype(int)
U['cohd']=(U.coh-D0).dt.days
C=pd.DataFrame(index=U.index); C['n']=1
for a in AGES:
    oa=o[o.age<=a].groupby('user_id').agg(ord=('order_id','size'),net=('net','sum'),mar=('margin','sum'),bad=('bad','sum'),ns=('ns','sum'))
    ga=g[g.age<=a].groupby('user_id').amount_paid.agg(['sum','size'])
    oa['net']+=ga['sum'].reindex(oa.index).fillna(0); oa['mar']+=ga['sum'].reindex(oa.index).fillna(0)
    oa['go']=(ga['size'].reindex(oa.index).fillna(0)>0).astype(int); oa['rep']=(oa.ord>=2).astype(int)
    for m in ['rep','ord','net','mar','bad','ns','go']: C[f'{m}{a}']=oa[m].reindex(C.index).fillna(0).values
MET=[c for c in C.columns]
def cube(dims):
    X=pd.concat([U[dims],C],axis=1).groupby(dims,observed=True).sum().reset_index()
    for c in MET: X[c]=X[c].round().astype(int)
    return X
K=cube(['cohd','acq','f_visit_purpose','disc','device','inapp','f_delay'])
R=cube(['cohd','region'])
# funnel
S['d']=(S.started_at_pl.dt.normalize()-D0).dt.days
fot=o[o.n==1].set_index('user_id').created_at
S['visitor']=np.where(S.uid.map(fot)<S.started_at_pl,'powracajacy','nowy')
def lp(p):
    if p.startswith('/blog'): return 'blog'
    if p.startswith('/specjalisci'): return 'specjalisci'
    return {'/':'home','/zwolnienie-l4-online':'l4','/lekarz-online':'lekarz','/recepta-online':'recepta','/konto':'konto','/polecenie':'polecenie','/telemedigo':'telemedigo'}.get(p,'inne')
S['lp']=S.landing_page.map(lp)
S['src']=np.where(S.utm_campaign.isin(PAID),S.utm_campaign,np.where(S.utm_campaign=='crm_go_upsell','crm_go_upsell',S.ch))
S['osb']=S.os+' / '+S.browser
st=['service_selected','slot_selected','account_completed','payment_started','payment_succeeded']
def fcube(fd):
    F=S.groupby(fd)[st].sum().astype(int); F.insert(0,'sess',S.groupby(fd).size()); return F.reset_index()
F1=fcube(['d','src','device','osb','visitor']); F2=fcube(['d','src','lp','visitor'])
print('K',len(K),'R',len(R),'F1',len(F1),'F2',len(F2))
# spend
sp['d']=(sp.date-D0).dt.days
SP=sp.groupby(['d','utm_campaign'])[['spend_pln','clicks','impressions']].sum().reset_index(); SP['spend_pln']=SP.spend_pln.round(2)
def enc(df):
    out={}
    for c in df.columns:
        if df[c].dtype==object or str(df[c].dtype).startswith('str') or str(df[c].dtype)=='category':
            vals=sorted(df[c].astype(str).unique()); m={v:i for i,v in enumerate(vals)}
            out[c]={'dict':vals,'idx':df[c].astype(str).map(m).tolist()}
        else: out[c]=df[c].tolist()
    return out
# wizyty: dzień terminu x pora x specjalizacja x pierwsza/kolejna (tylko odbyte)
v=o[o.started_at.notna()].copy(); v['dl']=(v.started_at-v.scheduled_at).dt.total_seconds()/60
hh=v.scheduled_at.dt.hour; v['pora']=np.select([hh<=5,hh<=11,hh<=17],['00-05','06-11','12-17'],'18-23')
v['d']=(v.scheduled_at.dt.normalize()-D0).dt.days; v=v[v.d.between(0,729)]
v['kind']=np.where(v.n==1,'pierwsza','kolejna'); v['l10']=(v.dl>10).astype(int); v['l20']=(v.dl>20).astype(int)
v['rs']=v.rating.fillna(0); v['rn']=v.rating.notna().astype(int)
VD=v.groupby(['d','pora','specialization','kind']).agg(vis=('order_id','size'),l10=('l10','sum'),l20=('l20','sum'),rs=('rs','sum'),rn=('rn','sum')).reset_index()
v['mo']=v.scheduled_at.dt.strftime('%Y-%m'); v['h']=hh
VH=v.groupby(['mo','h','specialization']).agg(vis=('order_id','size'),l20=('l20','sum'),rs=('rs','sum'),rn=('rn','sum')).reset_index()
for X in (VD,VH): X['rs']=X.rs.astype(int)
print('VD',len(VD),'VH',len(VH))
DATA={'d0':'2024-10-01','ndays':730,'ages':AGES,'K':enc(K),'R':enc(R),'F1':enc(F1),'F2':enc(F2),'SP':enc(SP),'VD':enc(VD),'VH':enc(VH)}
js=json.dumps(DATA,separators=(',',':'))
open('data.json','w').write(js); print('json MB',len(js)/1e6)
# control totals for verification
ctl={'patients':int(K.n.sum()),'orders365_all':None,'sessions':int(F1.sess.sum()),'paid_success':int(F1.payment_succeeded.sum()),'spend':round(float(SP.spend_pln.sum()),2),
     'orders_clean':int(len(o)),'visits_held':int((o.started_at.notna()&(o.scheduled_at<'2026-10-01')).sum()),'visits_after_axis':int((o.started_at.notna()&(o.scheduled_at>='2026-10-01')).sum()),'patients_P':int((U.per=='P').sum()),'patients_L':int((U.per=='L').sum())}
json.dump(ctl,open('control_totals.json','w'),indent=1); print(ctl)
