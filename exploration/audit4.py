import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev,users,orders,go,sp=[L(n) for n in 'ses ev users orders go sp'.split()]
o=orders
dup=o[o.duplicated(keep='first')]
print('dups by day'); print(dup.created_at.dt.date.value_counts().sort_index().to_string())
t=o[o.promo_code=='TEST-QA']
print('\nTEST-QA by month'); print(t.created_at.dt.to_period('M').value_counts().sort_index().to_string())
print(t[['amount_paid','list_price','status','refund_amount','specialization','payment_method']].describe(include='all').to_string())
print('TEST-QA users', t.user_id.nunique(), 'orders/user', t.groupby('user_id').size().describe().to_dict())
tu=users[users.user_id.isin(t.user_id)]; print(tu.head().to_string()); print('these users other orders', o[o.user_id.isin(t.user_id)&(o.promo_code!='TEST-QA')].shape[0])
ts=ses[ses.session_id.isin(t.session_id)]; print(ts.utm_source.value_counts(dropna=False).to_string(), ts.browser.value_counts().head().to_string(), ts.landing_page.value_counts().head().to_string())
print(t.created_at.dt.hour.value_counts().sort_index().to_string())
