import pandas as pd, numpy as np
pd.set_option('display.width',250)
L=lambda n: pd.read_pickle(n+'.pkl')
o,S=L('o'),L('Sc')
def span(df,t,cols):
    for c in cols:
        g=df.groupby(c,dropna=False)[t].agg(['min','max','count'])
        g=g[(g['min']>'2024-10-15')|(g['max']<'2026-09-15')]
        if len(g): print('==',c); print(g.to_string())
span(o,'created_at',['promo_code','specialization','visit_purpose','consultation_mode','payment_method','list_price'])
span(S,'started_at_pl',['utm_campaign','landing_page','browser','os','device','utm_source'])
# list price per spec by month
print(o.groupby([o.created_at.dt.to_period('Q'),'specialization']).list_price.agg(lambda s:sorted(s.unique())).unstack().to_string())
