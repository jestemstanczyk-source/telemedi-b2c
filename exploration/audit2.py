import pandas as pd
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev,users,orders,go,sp=[L(n) for n in 'ses ev users orders go sp'.split()]
print(pd.crosstab(ses.utm_source.fillna('(direct)'),ses.utm_medium.fillna('(none)')).to_string())
print('\n### EVENTS rows',len(ev))
print(ev.event_name.value_counts().to_string())
print('full dup', ev.drop(columns='_file').duplicated().sum())
dd=ev[ev.drop(columns='_file').duplicated(keep=False)]; print(dd._file.value_counts().to_string()); print(dd.sort_values(['session_id','event_name']).head(6).to_string())
print('dup sid+event (diff time)', ev.drop_duplicates(['session_id','event_name','event_at_utc']).duplicated(['session_id','event_name']).sum())
orph=~ev.session_id.isin(ses.session_id); print('orphan events',orph.sum(), ev[orph].event_name.value_counts().to_string())
print(ev[orph].event_at_utc.dt.to_period('M').value_counts().sort_index().to_string())
e=ev.drop_duplicates(['session_id','event_name','event_at_utc']).merge(ses[['session_id','started_at_utc']],on='session_id')
dt=(e.event_at_utc-e.started_at_utc).dt.total_seconds()
print('event before session start',(dt<0).sum(),' >24h after',(dt>86400).sum(), 'quantiles',dt.quantile([.5,.99,.999]).to_dict())
print(e[dt<0].event_at_utc.dt.to_period('M').value_counts().sort_index().to_string())
# order of steps
order={'service_selected':1,'slot_selected':2,'account_completed':3,'payment_started':4,'payment_succeeded':5}
e['k']=e.event_name.map(order)
w=e.pivot_table(index='session_id',columns='k',values='event_at_utc',aggfunc='min')
for a,b in [(1,2),(2,3),(3,4),(4,5),(2,4)]:
    m=w[a].notna()&w[b].notna(); print(f'step{a}>{b} out of order', (w.loc[m,a]>w.loc[m,b]).sum(),'of',m.sum())
# skip patterns
pat=w.notna().astype(int).astype(str).agg(''.join,axis=1); print(pat.value_counts().head(15).to_string())
