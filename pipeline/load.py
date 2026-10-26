import pandas as pd, glob
U='/mnt/user-data/uploads/'
ses=pd.concat([pd.read_csv(f,dtype={'visitor_id':str,'utm_source':str,'utm_medium':str,'utm_campaign':str}).assign(_file=f.split('/')[-1]) for f in sorted(glob.glob(U+'sessions_*.csv'))],ignore_index=True)
ev=pd.concat([pd.read_csv(f).assign(_file=f.split('/')[-1]) for f in sorted(glob.glob(U+'events_*.csv'))],ignore_index=True)
users=pd.read_csv(U+'users.csv'); orders=pd.read_csv(U+'orders.csv'); go=pd.read_csv(U+'go_memberships.csv'); sp=pd.read_csv(U+'marketing_spend.csv')
for df,c in [(ses,'started_at_utc'),(ev,'event_at_utc')]:
    df[c]=pd.to_datetime(df[c]); df[c.replace('_utc','_pl')]=df[c].dt.tz_localize('UTC').dt.tz_convert('Europe/Warsaw').dt.tz_localize(None)
for c in ['created_at','scheduled_at','started_at']: orders[c]=pd.to_datetime(orders[c])
users['registered_at']=pd.to_datetime(users['registered_at']); go['purchased_at']=pd.to_datetime(go['purchased_at']); sp['date']=pd.to_datetime(sp['date'])
for n,df in dict(ses=ses,ev=ev,users=users,orders=orders,go=go,sp=sp).items():
    df.to_pickle(f'{n}.pkl'); print(n,df.shape); print(df.dtypes.to_string()); print()
