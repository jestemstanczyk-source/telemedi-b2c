"""Niezależna weryfikacja: liczy sumy kontrolne prosto z surowych CSV (bez pipeline)
i porównuje z sumami zaszytymi w index.html. Uruchom: python verify.py <katalog_csv> <index.html>"""
import sys,glob,json,re,pandas as pd
d=sys.argv[1] if len(sys.argv)>1 else '/mnt/user-data/uploads'; html=sys.argv[2] if len(sys.argv)>2 else 'site/index.html'
o=pd.read_csv(d+'/orders.csv').drop_duplicates(); qa=set(o[o.promo_code=='TEST-QA'].user_id); o=o[~o.user_id.isin(qa)]
s=pd.concat([pd.read_csv(f,dtype=str) for f in glob.glob(d+'/sessions_*.csv')]); 
v2u=s.dropna(subset=['user_id']).groupby('visitor_id').user_id.first(); uid=s.user_id.fillna(s.visitor_id.map(v2u))
s=s[~uid.astype(float).isin(qa)]
e=pd.concat([pd.read_csv(f) for f in glob.glob(d+'/events_*.csv')]); ps=e[(e.event_name=='payment_succeeded')&e.session_id.astype(str).isin(s.session_id)]
sp=pd.read_csv(d+'/marketing_spend.csv')
mine={'patients':o.user_id.nunique(),'sessions':len(s),'paid_success':len(ps),'spend':round(sp.spend_pln.sum(),2),'orders_clean':len(o)}
t=open(html).read(); ctl=json.loads(re.search(r'window.CONTROL=(\{.*?\});',t,re.S).group(1))
ok=True
for k,v in mine.items(): r=abs(v-ctl[k])<0.5; ok&=r; print(f'{k:14s} CSV={v:>12} narzędzie={ctl[k]:>12}  {"OK" if r else "BŁĄD"}')
print('WYNIK:','zgodne' if ok else 'NIEZGODNE')
