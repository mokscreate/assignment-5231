import pandas as pd, json, re, sys
R='/home/claude/nsl/01_CURRENT/'
d=pd.read_csv(R+'NSL_Formal_Model/data.csv'); cov=pd.read_csv(R+'NSL_Review_Data/station_coverage.csv')
res=json.load(open(R+'NSL_Formal_Model/results.json'))
fr=pd.read_csv(R+'NSL_Formal_Model/factor_ranking.csv')
m=d[d.screening_status=='included']
st=[]
for _,c in cov.iterrows():
    u=c.source_url; mm=re.search(r'!3d(-?[\d.]+)!4d(-?[\d.]+)',u) or re.search(r'@(-?[\d.]+),(-?[\d.]+)',u)
    s=m[m.station_code==c.station_code]
    st.append(dict(code=c.station_code,name=c.station,lat=float(mm.group(1)),lng=float(mm.group(2)),
      displayed=int(c.displayed_total),collected=int(c.collected_records),text=int(c.text_records),
      model=len(s),aspects={a:int(s[a].sum()) for a in 'CMFVDTQAL'}))
def case(station,aspects,ids_low,ids_pos):
    s=m[(m.station==station)]
    fl=s[s[list(aspects)].sum(axis=1)>0]
    low=int((fl.rating<=2).sum()); hi=int((fl.rating>=4).sum()); mid=int((fl.rating==3).sum())
    def q(rid):
        r=fl[fl.review_id.str.startswith(rid)]
        assert len(r)==1,(rid,len(r)); r=r.iloc[0]
        return dict(id=r.review_id,rating=int(r.rating),when=r.displayed_date,text=str(r.review_text))
    return dict(flagged=len(fl),low=low,mid=mid,high=hi,neg=[q(i) for i in ids_low],pos=[q(i) for i in ids_pos])
json.dump(dict(stations=st,factors=fr.to_dict('records'),perf=res['performance'],scope=res['scope'],
  rating=res['rating_distribution'],screening=res['screening']),open('base.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(res['performance'],indent=0)[:900]); print(res['screening'],res['rating_distribution'])
# list candidate quotes with full prefixes for chosen cases
for stn,asp in [('Dhoby Ghaut','FV'),('Jurong East','DM'),('Kranji','Q')]:
    s=m[(m.station==stn)&(m[list(asp)].sum(axis=1)>0)]
    print('\n##',stn,len(s),(s.rating<=2).sum(),(s.rating==3).sum(),(s.rating>=4).sum())
    for _,r in s[s.rating>=4].head(14).iterrows(): print('POS',r.review_id[:16],r.rating,r.displayed_date,'|',str(r.review_text)[:200].replace('\n',' '))
