import pandas as pd, json, html, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
d=pd.read_csv(HERE.parent/'model'/'data.csv'); m=d[d.screening_status=='included']
HUMAN={r['review_id']:r for rs in json.load(open(HERE.parent/'annotation'/'human_coding'/'NSL_adjudication_final.json'))['rounds'].values() for r in rs}
def months(s):
    g=re.search(r'(\d+|a|an)\s+(year|month|week|day)',str(s))
    if not g: return None
    n=1 if g.group(1) in ('a','an') else int(g.group(1))
    return n*{'year':12,'month':1,'week':.25,'day':1/30}[g.group(2)]
base=json.load(open(HERE/'base.json'))
def pick(station,aspects,prefixes):
    s=m[(m.station==station)]; fl=s[s[list(aspects)].sum(axis=1)>0]
    out=[]
    for p in prefixes:
        r=fl[fl.review_text.fillna('').str.startswith(p)]
        assert len(r)>=1,(station,p); r=r.iloc[0]
        t=str(r.review_text).replace('\n',' ').strip()
        if len(t)>190: t=t[:187].rsplit(' ',1)[0]+'…'
        out.append(dict(id=r.review_id,rating=int(r.rating),when=r.displayed_date,text=t))
    for q in out:
        h=HUMAN.get(q['id'])
        if h: q['human']=h['scope']+'; '+', '.join(f"{k} {v}" for k,v in h['aspects'].items() if v!='absent')
    ages=[a for a in fl.displayed_date.map(months) if a is not None]
    return dict(flagged=len(fl),low=int((fl.rating<=2).sum()),mid=int((fl.rating==3).sum()),high=int((fl.rating>=4).sum()),
                station_model=len(s),station_low=int((s.rating<=2).sum()),
                period=dict(min_months=round(min(ages),1),max_months=round(max(ages)),within_2y=int(sum(a<=24 for a in ages)),dated=len(ages)),q=out)
cases={
 'NS24':dict(station='Dhoby Ghaut',aspects='FV',theme='Wayfinding in a large three-line interchange',
   complaint='Reviewers describe the interchange as convoluted, say exits are hard to identify, and ask for exit numbers in directions.',
   neg=pick('Dhoby Ghaut','FV',["It's incredibly convoluted","Confusing. Got lost.","For directions from dhoby ghaut","So complicated so many escalators"]),
   pos=pick('Dhoby Ghaut','FV',["Super big mrt. Sometimes too many exits","The station was clean and comfortable"]),
   proposal='Candidate change: add the exit number or destination (e.g. Plaza Singapura, Fort Canning) to line-transfer direction signs at the main decision points.',
   evaluate='A site check should first confirm where people hesitate. To test the change, time one fixed task (NS line to Plaza Singapura exit) for first-time users before and after, and count wrong turns.'),
 'NS1':dict(station='Jurong East',aspects='FDM',theme='Crowding, platform changes and construction detours',
   complaint='Complaints mix peak-hour crowding with confusion about which platform a train uses and unclear signs to Jurong Central and the malls during construction.',
   neg=pick('Jurong East','FDM',["very confusing every time a train arrives","heavy construction ongoing","That directional sign doesn't have a large sign","Too crowded n a dangerous place for seniors"]),
   pos=pick('Jurong East','FDM',["Spacious. Clean and tidy.","Great connectivity to malls"]),
   proposal='Candidate change: show the arriving platform earlier on the concourse and add a large destination sign on the construction-period route to the malls. Crowding needs peak-hour observation before any physical change is proposed.',
   evaluate='Compare wrong-turn counts and platform-change confusion at peak hours before and after. Many complaints are old and may describe layouts that have since changed.'),
 'NS7':dict(station='Kranji',aspects='Q',theme='Odour, bins and toilet upkeep',
   complaint='Several reviews describe smell and dirt around the bin area, the toilets and the station exit.',
   neg=pick('Kranji','Q',["filthy toilet!","Dirty, smells of urine","Bin center too smelly","@SMRT kindly look at the bin area"]),
   pos=pick('Kranji','Q',["Clean place and there is direction","Kranji MRT station is a convenient and well-maintained"]),
   proposal='Candidate change: check the cleaning schedule and consumables at peak flow times, and the location of the bin area relative to the station entrance. The bin area is described as behind a nearby building and may not be station-managed.',
   evaluate='Compare inspection logs or the count of odour and cleanliness complaints before and after. A site check should first confirm who manages the bin area.')}
for k,v in cases.items(): v['code']=k
# station code check
codes={s['name']:s['code'] for s in base['stations']}
for k,v in cases.items(): assert codes[v['station']]==k,(k,codes[v['station']])
base['cases']=cases
_pol=json.load(open(HERE.parent/'model'/'polarity_results.json'))
_val=json.load(open(HERE.parent/'model'/'polarity_validation.json'))['test_vs_human_adjudicated_100']
_pc,_pl=_pol['polarity_counts'],_pol['polarity_counts_rated_1_3']
base['polarity']={'perf':{k:v['mean_repeated_group_cv'] for k,v in _pol['performance'].items()},
  'top3':{m:{k:v['share_top3'] for k,v in _pol['importance_and_rank_uncertainty'][m].items()} for m in ('B_mention_logistic','B_mention_forest','C_polarity_logistic','C_polarity_forest')},
  'neg':{k:[_pc[k]['negative'],_pl[k]['negative']] for k in _pc},
  'paired':{k:v['station_bootstrap_95_ci']+[v['auc_difference']] for k,v in _pol['paired_auc_difference'].items()},
  'val':{'n':_val['aspect_instances_compared'],'raw':_val['raw_agreement'],'kappa':_val['cohen_kappa'],'neg':_val['negative_recall'],'pos':_val['positive_recall']}}
json.dump(base,open(HERE/'site_data.json','w',encoding='utf-8'),ensure_ascii=False)
for k,v in cases.items(): print(k,v['station'],v['neg']['flagged'],v['neg']['low'],v['neg']['mid'],v['neg']['high'])

Path(HERE/'results_site.html').write_text((HERE/'template.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(base,ensure_ascii=False)),encoding='utf-8')
# Chinese review version (English site is the master)
zh=json.load(open(HERE/'cases_zh.json',encoding='utf-8'));zh.pop('_note',None)
Path(HERE/'results_site_zh.html').write_text((HERE/'template_zh.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps({**base,'zh':zh},ensure_ascii=False)),encoding='utf-8')

