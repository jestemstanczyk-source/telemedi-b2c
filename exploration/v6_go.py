import pandas as pd, numpy as np
go=pd.read_pickle('goc.pkl').sort_values('purchased_at').copy()   # bez kont QA
go['vu']=pd.to_datetime(go.valid_until)
go['nth']=go.groupby('user_id').cumcount()+1
first=go[go.nth==1].set_index('user_id')
nxt=go[go.nth==2].set_index('user_id').purchased_at
first['next']=nxt.reindex(first.index)
E=first[first.vu<='2026-07-31'].copy()   # pierwsze członkostwa wygasłe do końca lipca 2026
E['gap']=(E.next-E.vu).dt.days
print('pierwszych członkostw wygasłych do VII 2026:',len(E))
print('Def. szeroka (prompt): nowe GO w dowolnym momencie po 1. zakupie:',E.next.notna().sum(),f'= {E.next.notna().mean():.2%}')
print('kupione przed wygaśnięciem (nakładające się):',(E.next<=E.vu).sum())
for w in [0,30,60,90]: print(f'Def. ścisła: kupione ≤{w} dni po wygaśnięciu:',(E.gap.between(-10**4,w)).sum(),f'= {(E.gap<=w).mean():.2%}')
print('rozkład gap (dni od wygaśnięcia do nowego GO):',E.gap.dropna().describe().round(1).to_dict())
# okno obserwacji: ile dni od wygaśnięcia do końca danych
E['obs']=(pd.Timestamp('2026-09-30')-E.vu).dt.days; print('min dni obserwacji po wygaśnięciu',E.obs.min(),' mediana',E.obs.median())
E['qe']=E.vu.dt.to_period('Q'); print(E.groupby('qe').next.apply(lambda s:s.notna().mean()).round(3).to_string())
# z wszystkich członkostw (nie tylko pierwszych)
A=go[go.vu<='2026-07-31'].copy(); A['nxt']=go.groupby('user_id').purchased_at.shift(-1).reindex(A.index); print('wszystkie wygasłe członkostwa',len(A),'z następnym GO',A.nxt.notna().mean().round(4))
