"""Expanded-corpus models. Automatic aspect coding is NOT human ground truth.
Run: python model.py. All paths are relative to this file.
"""
from pathlib import Path
import csv, json, re, hashlib, platform
import numpy as np
import sklearn, joblib
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score, f1_score, balanced_accuracy_score, accuracy_score

ROOT=Path(__file__).resolve().parent
SEED=5231
# Fixed before testing the expanded corpus. Presence only, not sentiment.
ASPECTS={
 'C':('Station-city connectivity',r'\b(?:connect\w*|interchange|accessible|accessibility|bus(?:es)?|malls?|shopping cent(?:re|er)s?|nearby|linked|linkways?|convenient location|centrally located|central location)\b|连接|接驳|商场|公交|巴士|区位|周边|可达'),
 'M':('Walking and transfer paths',r'\b(?:walk\w*|corridors?|passage\w*|underpass\w*|overpass\w*|footbridge\w*|footpath\w*|walkway\w*|transfer\w*|platforms?|gates?|gantr(?:y|ies)|detours?)\b|步行|通道|换乘|月台|站台|闸机|绕路'),
 'F':('Wayfinding and signage',r'\b(?:signs?|signage|directions?|directional|directories|directory|maps?|exits?|entrances?|confus\w*|lost|navigat\w*|wayfinding)\b|标识|标志|指引|指示|迷路|找路|出口|入口|导向|地图'),
 'V':('Vertical circulation and accessibility',r'\b(?:lifts?|elevators?|escalators?|stairs?|staircase\w*|wheelchair\w*|prams?|strollers?|ramps?|barrier.free|disabled|disabilit\w*)\b|电梯|扶梯|楼梯|轮椅|无障碍|坡道|婴儿车'),
 'D':('Crowding and pedestrian flow',r'\b(?:crowd\w*|congest\w*|queues?|queuing|queueing|packed|rush hour|peak hours?|busy|spacious|cramped|empty)\b|拥挤|人流|人多|人少|排队|宽敞|狭窄'),
 'T':('Thermal comfort, air and shelter',r'\b(?:hot|heat|warm|cold|cool\w*|fans?|air.con\w*|air condition\w*|ventilat\w*|stuffy|humid\w*|shelter\w*|covered|rain\w*|shade\w*|sunny|sunlight|breez\w*)\b|炎热|闷热|凉爽|空调|通风|风扇|遮雨|遮阳|淋雨|遮蔽'),
 'Q':('Cleanliness and maintenance',r'\b(?:clean\w*|dirty|dirt|filthy|hygien\w*|smell\w*|odor\w*|odour\w*|stink\w*|litter\w*|rubbish|maintain\w*|maintenance|broken|repair\w*|leak\w*|renovat\w*)\b|干净|清洁|卫生|脏|异味|臭|垃圾|损坏|维修|维护|漏水|翻新'),
 'A':('Amenities and dwell support',r'\b(?:shops?|shopping|foods?|restaurants?|eater\w*|hawker\w*|cafes?|coffee|toilets?|restrooms?|washrooms?|bathrooms?|seats?|seating|benches|bench|amenities|amenity|atms?|banks?|retail|resting)\b|商店|购物|餐厅|餐饮|食物|小贩|厕所|卫生间|洗手间|座椅|休息|银行|便利店'),
 'L':('Lighting and spatial ambience',r'\b(?:lighting|bright|dark|dim|design\w*|architect\w*|decor\w*|ambien\w*|aesthe\w*|artworks?|art|scenic|scenery|landscap\w*|views?|beautiful|greenery)\b|照明|光线|明亮|昏暗|设计|建筑|装饰|氛围|景观|绿化|艺术')}
KEYS=list(ASPECTS)
RULES={k:re.compile(p,re.I) for k,(_,p) in ASPECTS.items()}
def normalize(t):return re.sub(r'[^\w]+',' ',t.casefold(),flags=re.UNICODE).strip()
def encode(t):return [int(bool(RULES[k].search(t))) for k in KEYS]
def text_input(t,stations):
    t=re.sub(r'\b(?:[1-5]|one|two|three|four|five)\s*(?:out of\s*(?:5|five)|[/]5|[- ]?stars?)\b',' ',t,flags=re.I)
    for s in sorted(stations,key=len,reverse=True):t=re.sub(re.escape(s),' station ',t,flags=re.I)
    return t
def metrics(y,p):
    pred=(p>=.5).astype(int)
    return {'auc':float(roc_auc_score(y,p)),'macro_f1':float(f1_score(y,pred,average='macro',zero_division=0)),'balanced_accuracy':float(balanced_accuracy_score(y,pred)),'accuracy':float(accuracy_score(y,pred))}
def ci(v):return [float(x) for x in np.percentile(v,[2.5,97.5])]
def main():
    rows=list(csv.DictReader((ROOT/'data.csv').open(encoding='utf-8-sig')))
    stations=sorted({r['station'] for r in rows})
    seen,included,reasons=set(),[],{}
    for r in rows:
        t=r['review_text'].strip();key=normalize(text_input(t,stations));flags=encode(t)
        if not t:reason='rating_only'
        elif not key:reason='no_lexical_text'
        elif key in seen:reason='duplicate_normalized_text'
        elif not any(flags):reason='no_dictionary_spatial_match'
        else:reason='included'
        if key:seen.add(key)
        reasons[reason]=reasons.get(reason,0)+1
        r.update({k:str(v) for k,v in zip(KEYS,flags)})
        r['screening_status']=reason;r['coding_method']='fixed_bilingual_dictionary_unverified'
        r['spatial_coding_status']='automatic_dictionary_unverified' if t else 'not_applicable_rating_only'
        if reason=='included':included.append(r)
    X=np.array([[int(r[k]) for k in KEYS] for r in included])
    y=np.array([int(r['rating'])>=4 for r in included],dtype=int)
    groups=np.array([r['station'] for r in included])
    texts=np.array([text_input(r['review_text'],stations) for r in included])
    assert len(np.unique(groups))>=5 and np.bincount(y).min()>=30
    constructors={
      'MajorityBaseline':lambda:DummyClassifier(strategy='prior'),
      'SpatialLogisticRegression':lambda:LogisticRegression(C=1,class_weight='balanced',max_iter=2000,random_state=SEED),
      'SpatialRandomForest':lambda:RandomForestClassifier(n_estimators=250,max_depth=8,min_samples_leaf=10,class_weight='balanced_subsample',random_state=SEED,n_jobs=2),
      'TextTFIDFLogisticRegression':lambda:make_pipeline(TfidfVectorizer(ngram_range=(1,2),min_df=3,max_df=.98,max_features=20000,sublinear_tf=True),LogisticRegression(C=1,class_weight='balanced',max_iter=2000,random_state=SEED))}
    oof={name:np.zeros((3,len(y))) for name in constructors}
    shuffled={name:np.zeros((6,len(y),len(KEYS))) for name in ['SpatialLogisticRegression','SpatialRandomForest']}
    folds=[]
    for repeat in range(3):
      for fold,(train,test) in enumerate(StratifiedGroupKFold(5,shuffle=True,random_state=SEED+repeat).split(X,y,groups)):
        assert not(set(groups[train])&set(groups[test]))
        assert not(set(normalize(texts[i]) for i in train)&set(normalize(texts[i]) for i in test))
        folds.append({'repeat':repeat,'fold':fold,'test_stations':sorted(set(groups[test])),'test_n':len(test)})
        for name,ctor in constructors.items():
          inp=texts if name.startswith('Text') else X
          m=ctor().fit(inp[train],y[train]);oof[name][repeat,test]=m.predict_proba(inp[test])[:,1]
          if repeat==0 and name in shuffled:
            rng=np.random.default_rng(SEED+fold)
            for col in range(len(KEYS)):
              for perm in range(6):
                xp=X[test].copy()
                for s in np.unique(groups[test]):
                  ix=np.flatnonzero(groups[test]==s);xp[ix,col]=rng.permutation(xp[ix,col])
                shuffled[name][perm,test,col]=m.predict_proba(xp)[:,1]
        print(f'Completed repeat {repeat+1}/3, station fold {fold+1}/5',flush=True)
    rng=np.random.default_rng(SEED);gs=np.unique(groups)
    bootstrap=[np.concatenate([np.flatnonzero(groups==s) for s in rng.choice(gs,len(gs),replace=True)]) for _ in range(300)]
    performance={}
    for name,p in oof.items():
      per=[metrics(y,v) for v in p];draws=[metrics(y[ix],p[0,ix]) for ix in bootstrap]
      performance[name]={'mean_repeated_group_cv':{k:float(np.mean([m[k] for m in per])) for k in per[0]},'repeat_metrics':per,'first_repeat_station_bootstrap_95_ci':{k:ci([d[k] for d in draws]) for k in per[0]}}
    factors=[]
    for col,k in enumerate(KEYS):
      r={'code':k,'factor':ASPECTS[k][0],'mentions':int(X[:,col].sum()),'mention_percent':float(100*X[:,col].mean())}
      for name,short in [('SpatialLogisticRegression','logistic'),('SpatialRandomForest','forest')]:
        p=oof[name][0];q=shuffled[name][:,:,col]
        r[short+'_auc_drop']=float(roc_auc_score(y,p)-np.mean([roc_auc_score(y,v) for v in q]))
        draws=[roc_auc_score(y[ix],p[ix])-np.mean([roc_auc_score(y[ix],v[ix]) for v in q]) for ix in bootstrap]
        r[short+'_ci_low'],r[short+'_ci_high']=ci(draws)
      factors.append(r)
    for metric,prefix in [('mentions','frequency'),('logistic_auc_drop','logistic_importance'),('forest_auc_drop','forest_importance')]:
      for r in factors:r[prefix+'_rank']=1+sum(v[metric]>r[metric] for v in factors)
    keep=np.array([int(r['rating'])!=3 for r in included]);sx,sy,sg=X[keep],y[keep],groups[keep];sp=np.zeros(len(sy))
    for train,test in StratifiedGroupKFold(5,shuffle=True,random_state=SEED).split(sx,sy,sg):
      m=constructors['SpatialLogisticRegression']().fit(sx[train],sy[train]);sp[test]=m.predict_proba(sx[test])[:,1]
    fitted={name:ctor().fit(texts if name.startswith('Text') else X,y) for name,ctor in constructors.items() if name!='MajorityBaseline'}
    joblib.dump({'models':fitted,'feature_order':KEYS,'feature_names':{k:v[0] for k,v in ASPECTS.items()},'patterns':{k:v[1] for k,v in ASPECTS.items()},'stations':stations,'target':'4-5 stars versus 1-3 stars','annotation_status':'automatic dictionary, not human validated','sklearn_version':sklearn.__version__},ROOT/'trained_models.joblib',compress=3)
    unique_partitions=len({tuple(sorted(tuple(f['test_stations']) for f in folds if f['repeat']==r)) for r in range(3)})
    summary={'scope':'Expanded-corpus models; automatic coding, not a validated final research conclusion','raw_records':len(rows),'text_records':sum(bool(r['review_text'].strip()) for r in rows),'screening':reasons,'model_records':len(y),'model_stations':len(gs),'rating_distribution':{str(k):sum(int(r['rating'])==k for r in included) for k in range(1,6)},'performance':performance,'neutral_excluded_sensitivity':{'n':len(sy),**metrics(sy,sp)},'unique_group_partitions':unique_partitions,'folds':folds,'factors':factors,'software':{'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__}}
    for i,r in enumerate(included):
      for name in oof:r['oof_'+name]=str(float(oof[name][0,i]))
    fields=list(dict.fromkeys(list(rows[0])+['oof_'+name for name in oof]))
    with (ROOT/'data.csv').open('w',encoding='utf-8-sig',newline='') as f:
      w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    summary['coded_data_sha256']=hashlib.sha256((ROOT/'data.csv').read_bytes()).hexdigest()
    (ROOT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    with (ROOT/'factor_ranking.csv').open('w',encoding='utf-8-sig',newline='') as f:
      w=csv.DictWriter(f,fieldnames=list(factors[0]));w.writeheader();w.writerows(sorted(factors,key=lambda x:x['logistic_importance_rank']))
    print(json.dumps({'screening':reasons,'n':len(y),'performance':{k:v['mean_repeated_group_cv'] for k,v in performance.items()},'sensitivity':summary['neutral_excluded_sensitivity']},indent=2),flush=True)
def predict(text):
    bundle=joblib.load(ROOT/'trained_models.joblib')
    x=np.array([encode(text)])
    scores={name:float(m.predict_proba([text_input(text,bundle['stations'])] if name.startswith('Text') else x)[0,1]) for name,m in bundle['models'].items()}
    print(json.dumps({'detected_aspects':[ASPECTS[k][0] for k,v in zip(KEYS,x[0]) if v],
      'high_rating_scores':scores,'note':'Uncalibrated model scores, not causal effects or guaranteed probabilities. Spatial models should not be interpreted when no spatial aspects are detected.'},indent=2))
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--predict',type=str)
    args=parser.parse_args()
    if args.predict is not None:predict(args.predict)
    else:main()
