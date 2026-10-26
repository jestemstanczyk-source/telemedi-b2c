import pandas as pd
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev,users,orders,go,sp=[L(n) for n in 'ses ev users orders go sp'.split()]
print('### SESSIONS')
print('rows',len(ses),'uniq sid',ses.session_id.nunique(),'full dup rows',ses.drop(columns='_file').duplicated().sum())
d=ses[ses.session_id.duplicated(keep=False)].sort_values('session_id'); print('dup sid rows',len(d)); print(d.head(6).to_string())
print(d._file.value_counts().head())
print('range utc',ses.started_at_utc.min(),ses.started_at_utc.max())
# file boundary check: does file quarter match UTC or PL?
ses['q_utc']=ses.started_at_utc.dt.to_period('Q').astype(str); ses['q_pl']=ses.started_at_pl.dt.to_period('Q').astype(str)
print(pd.crosstab(ses._file,ses.q_utc).to_string())
for c in ['utm_source','utm_medium','device','os','browser','landing_page']: print(ses[c].value_counts(dropna=False).to_string(),'\n')
print('logged share',ses.user_id.notna().mean())
print('visitor per user', ses.dropna(subset=['user_id']).groupby('user_id').visitor_id.nunique().describe())
print('users per visitor', ses.dropna(subset=['user_id']).groupby('visitor_id').user_id.nunique().value_counts().head())
print('orphan user in ses', (~ses.user_id.dropna().isin(users.user_id)).sum())
