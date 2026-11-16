from pathlib import Path
import json,csv,collections,re,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2];TMP=ROOT/'tmp/annotation_review';OUT=ROOT/'output/NSL_Annotation_Review'
blind={r['audit_id']:r for r in json.loads((TMP/'blind.json').read_text(encoding='utf-8'))}
private={r['audit_id']:r for r in json.loads((TMP/'private_key.json').read_text(encoding='utf-8'))}
labels=[]
for f in sorted(TMP.glob('labels_*.json')):labels.extend(json.loads(f.read_text(encoding='utf-8')))
assert len(labels)==200 and len({r[0] for r in labels})==200
KEYS=list('CMFVDTQAL');valences={'+':'positive','-':'negative','0':'neutral','~':'mixed','?':'uncertain'}
annotations=[];mismatches=[]
for ident,scope,codes,evidence,note,check in labels:
    b=blind[ident];p=private[ident];labs={k:'absent' for k in KEYS}
    for pair in codes.split():
        assert len(pair)==2 and pair[0] in KEYS and pair[1] in valences
        labs[pair[0]]=valences[pair[1]]
    pieces=evidence.split(' | ')
    for quote in pieces:
        if quote.casefold() not in b['text'].casefold():mismatches.append([ident,quote])
    # Stronger masks after two residual in-text rating disclosures were noticed.
    text=b['text']
    if ident=='R133':text=re.sub(r'I was planning.*','[rating-related sentence hidden]',text,flags=re.S)
    if ident=='R176':text=text.replace('1 extra star','[rating phrase hidden]')
    if ident=='R073':text='[numeric-only content hidden]'
    annotations.append({'audit_id':ident,'station':b['station'],'review_id':p['review_id'],'source_url':p['source_url'],
      'review_text_blinded':text,'scope_ai':scope,'aspects_ai':labs,'evidence_ai':pieces,'rationale_ai':note,
      'needs_adjudication':check,'blinding_note':'Residual rating language noticed during first pass; excluded from agreement subset.' if ident in ['R133','R176'] else 'Original star field and previous labels hidden during AI annotation.',
      'annotation_status':'single_AI_initial_annotation_not_human_verified','human_scope':'','human_aspects':{},'human_notes':''})
assert not mismatches, mismatches
# Agreement only, NOT accuracy against human gold labels. Exclude flagged ambiguity.
clear=[a for a in annotations if not a['needs_adjudication'] and a['audit_id'] not in ['R133','R176']]
def counts(pairs):
    tp=sum(p and y for p,y in pairs);fp=sum(p and not y for p,y in pairs);fn=sum(not p and y for p,y in pairs);tn=sum(not p and not y for p,y in pairs)
    return {'n':len(pairs),'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision_agreement':tp/(tp+fp) if tp+fp else None,'recall_agreement':tp/(tp+fn) if tp+fn else None}
scope_pairs=[(any(private[a['audit_id']][k]=='1' for k in KEYS),a['scope_ai']=='station_spatial') for a in clear]
factor_stats={}
for k in KEYS:
    factor_stats[k]=counts([(private[a['audit_id']][k]=='1',a['scope_ai']=='station_spatial' and a['aspects_ai'][k] not in ['absent','uncertain']) for a in clear])
summary={'sample_n':200,'stations':len({a['station'] for a in annotations}),
 'sample_design':'Seed 5231200; round-robin station x rating-band x dictionary-hit strata; nonempty unique normalised text. Disproportionate diagnostic sample, not population prevalence.',
 'scope_counts':dict(collections.Counter(a['scope_ai'] for a in annotations)),
 'needs_adjudication':sum(a['needs_adjudication'] for a in annotations),
 'annotation_method':'One AI read all 200 texts with star field and old feature labels withheld; no independent human or second-rater validation.',
 'known_partial_blinding_records':['R133','R176'],
 'agreement_subset_n':len(clear),'dictionary_vs_AI_scope_agreement':counts(scope_pairs),
 'dictionary_vs_AI_aspect_agreement':factor_stats,
 'polarity_counts_station_spatial':dict(collections.Counter(v for a in annotations if a['scope_ai']=='station_spatial' for v in a['aspects_ai'].values() if v!='absent')),
 'interpretation':'Agreement with AI is diagnostic only. Sampling weights are not applied. Do not extrapolate these rates to the full corpus, publish them as human accuracy, or use this selected sample as a final model test set.'}
(OUT/'annotations.json').write_text(json.dumps(annotations,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'audit_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
