from pathlib import Path
import csv,json,random,re,collections
ROOT=Path(__file__).resolve().parents[2]
rows=list(csv.DictReader((ROOT/'output/NSL_Formal_Model/data.csv').open(encoding='utf-8-sig')))
rng=random.Random(5231200);seen=set();strata=collections.defaultdict(list)
for r in rows:
 t=r['review_text'].strip();key=re.sub(r'[^\w]+',' ',t.casefold()).strip()
 if not key or key in seen:continue
 seen.add(key)
 band='low' if int(r['rating'])<=2 else 'neutral' if int(r['rating'])==3 else 'high'
 detected=any(r[k]=='1' for k in 'CMFVDTQAL')
 strata[(r['station'],band,detected)].append(r)
for v in strata.values():rng.shuffle(v)
keys=list(strata);rng.shuffle(keys);sample=[]
while len(sample)<200:
 for k in keys:
  if strata[k]:sample.append(strata[k].pop())
  if len(sample)==200:break
rng.shuffle(sample)
private=[];blind=[]
for i,r in enumerate(sample,1):
 ident=f'R{i:03}'
 t=re.sub(r'\b(?:[1-5]|one|two|three|four|five)\s*(?:out of\s*(?:5|five)|[/]5|[- ]?stars?)\b','[rating phrase hidden]',r['review_text'],flags=re.I)
 private.append({'audit_id':ident,**r})
 blind.append({'audit_id':ident,'station':r['station'],'text':t})
p=ROOT/'tmp/annotation_review'
(p/'private_key.json').write_text(json.dumps(private,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'blind.json').write_text(json.dumps(blind,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared 200 rating-blind records across',len({r['station'] for r in sample}),'stations. Original labels and scores withheld from annotator.')
