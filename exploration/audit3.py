import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
ses,ev,users,orders,go,sp=[L(n) for n in 'ses ev users orders go sp'.split()]
o=orders
print('rows',len(o),'uniq oid',o.order_id.nunique())
print('full dup',o.duplicated().sum(),' dup excl order_id',o.drop(columns='order_id').duplicated().sum())
dk=o[o.drop(columns='order_id').duplicated(keep=False)]; print(dk.head(6).to_string())
print('orphan user',(~o.user_id.isin(users.user_id)).sum())
print('session null',o.session_id.isna().sum(),' session not in ses',(o.session_id.notna()&~o.session_id.isin(ses.session_id)).sum())
print('sessions with >1 order', o.session_id.value_counts().gt(1).sum())
for c in ['specialization','visit_purpose','consultation_mode','discount_type','payment_method','status','promo_code','list_price']: print(o[c].value_counts(dropna=False).head(25).to_string(),'\n')
print(pd.crosstab(o.specialization,o.list_price).to_string())
