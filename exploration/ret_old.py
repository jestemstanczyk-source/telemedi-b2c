import pandas as pd, numpy as np
L=lambda n: pd.read_pickle(n+'.pkl')
U,S,o=L('U'),L('Sc'),L('o')
end=pd.Timestamp('2026-09-30')
old=~U.ch.isin(['meta/paid_social','tiktok/paid_social'])
M=U[old&(U.coh<=end-pd.Timedelta(days=60))].copy(); M['r60']=M.d2<=60
fos=S.set_index('session_id').loc[o[o.n==1].set_index('user_id').session_id.reindex(M.index)]
M['ios_saf']=((fos.os=='iOS')&(fos.browser=='Safari')).values
M['q']=M.coh.dt.to_period('Q')
print(M.pivot_table(index='q',columns='ios_saf',values='r60',aggfunc='mean').round(3).to_string())
print(M.pivot_table(index='q',columns='ios_saf',values='r60',aggfunc='size').to_string())
# repeat-order sessions of returning users: account step conversion iOS safari
