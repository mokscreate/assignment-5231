import pandas as pd, json
R='/home/claude/nsl/01_CURRENT/'
d=pd.read_csv(R+'NSL_Formal_Model/data.csv'); m=d[d.screening_status=='included']
base=json.load(open('base.json'))
def q(station,prefix):
    s=m[(m.station==station)&m.review_text.fillna('').str.startswith(prefix)]
    assert len(s)>=1,(station,prefix); r=s.iloc[0]; t=str(r.review_text).replace('\n',' ').strip()
    if len(t)>170:t=t[:167].rsplit(' ',1)[0]+'…'
    return dict(text=t,id=r.review_id,station=station,rating=int(r.rating),when=r.displayed_date)
quotes=dict(F=q('Dhoby Ghaut','Confusing. Got lost.'),D=q('Jurong East','Always packed like sardines'),
 Q=q('Kranji','Bin center too smelly'),M=q('Jurong East','very confusing every time a train arrives'),
 V=q('Dhoby Ghaut','So complicated so many escalators'))
pct={f['code']:round(f['mention_percent'],1) for f in base['factors']}
st=[dict(code=s['code'],name=s['name'],lat=s['lat'],lng=s['lng'],model=s['model'],text=s['text'],aspects=s['aspects']) for s in base['stations']]
json.dump(dict(stations=st,quotes=quotes,pct=pct),open('game_data.json','w'),ensure_ascii=False)
print(quotes)
