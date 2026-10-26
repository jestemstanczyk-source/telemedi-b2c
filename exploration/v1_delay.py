import pandas as pd, numpy as np
pd.set_option('display.width',250)
o=pd.read_pickle('o.pkl')
# Definicja: wizyty internisty, które się odbyły (started_at niepuste: completed+refunded); opóźnienie = started_at - scheduled_at w minutach
x=o[(o.specialization=='internista')&o.started_at.notna()].copy()
x['delay']=(x.started_at-x.scheduled_at).dt.total_seconds()/60
h=x.scheduled_at.dt.hour
x['slot']=np.select([h.between(6,11),h.between(12,17),h.between(18,23)],['06-11','12-17','18-23'],'00-05')
x['late20']=x.delay>20
x['m']=x.scheduled_at.dt.to_period('M')
print('wizyt',len(x),' rozkład opóźnienia',x.delay.describe().round(1).to_dict())
print('\nOdsetek >20 min: miesiąc x pora');print((x.pivot_table(index='m',columns='slot',values='late20',aggfunc='mean')*100).round(1).to_string())
print('\nLiczba wizyt');print(x.pivot_table(index='m',columns='slot',values='late20',aggfunc='size').to_string())
print('\nŚrednia ocena: miesiąc x pora');print(x.pivot_table(index='m',columns='slot',values='rating',aggfunc='mean').round(2).to_string())
print('\nOcena wg opóźnienia');x['db']=pd.cut(x.delay,[-10,5,10,20,40,400]);print(x.groupby('db',observed=True).rating.agg(['mean','count']).round(2).to_string())
x.to_pickle('x_int.pkl')
