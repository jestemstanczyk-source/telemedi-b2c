import pandas as pd, numpy as np
o=pd.read_pickle('o.pkl')
x=o[(o.created_at>='2025-10-01')&(o.created_at<'2026-10-01')].copy()
DOC={'internista':25,'psychiatra':200}
x['doc']=np.where(x.status.isin(['completed','refunded']),x.specialization.map(DOC).fillna(100),0)
x['m']=x.amount_paid-x.refund_amount-x.doc   # bez opłaty GO (ta nie jest przychodem z wizyty)
A=x.pivot_table(index='specialization',columns='discount_type',values='m',aggfunc='mean').round(1)
N=x.pivot_table(index='specialization',columns='discount_type',values='m',aggfunc='size')
T=x.pivot_table(index='specialization',columns='discount_type',values='m',aggfunc='sum').round(0)
print('Definicja A: na zamówienie (wszystkie statusy)'); print(A.to_string()); print(N.to_string())
h=x[x.status.isin(['completed','refunded'])]
B=h.pivot_table(index='specialization',columns='discount_type',values='m',aggfunc='mean').round(1)
print('\nDefinicja B: na odbytą wizytę (completed+refunded)'); print(B.to_string())
neg=A.stack().loc[lambda s:s<0]; print('\nUjemne (def. A):',len(neg)); print(pd.DataFrame({'marża_śr':neg,'n':N.stack()[neg.index],'suma_zł':T.stack()[neg.index]}).sort_values('suma_zł').to_string())
print('Suma strat w ujemnych komórkach:',T.stack()[neg.index].sum())
print('\nCałość: marża/zamówienie',x.m.mean().round(1),' suma',x.m.sum().round(0))
