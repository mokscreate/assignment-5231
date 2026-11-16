"""Inter-coder agreement for the round-1 (60-record) or round-2 (40-record) overlap.

Usage: python agreement_overlap60.py CODER1.json CODER2.json
The round is detected from the export schema (nsl-overlap60-v1 or nsl-round2-v1).
Reads the two original (pre-discussion) exports. Reports raw agreement and
Cohen's kappa with class counts for: scope (7 classes), spatial vs non-spatial,
each aspect's mention (absent vs discussed), and each aspect's polarity on records
both coders marked as discussed. Writes:
  agreement_overlap60.json      all statistics
  adjudication_overlap60.csv    both original labels side by side + blank adjudicated columns
The input files are never modified.
"""
import csv, json, sys, collections
from pathlib import Path

ASPECTS = 'CMFVDTQAL'
ROUNDS = {'nsl-overlap60-v1': ('overlap60_blind.json', 'overlap60'), 'nsl-round2-v1': ('round2_blind.json', 'round2')}
SCOPES = ['station_spatial', 'station_operations_only', 'train_interior', 'surroundings_only', 'off_topic', 'generic', 'unclear']


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None, None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (None if pe == 1 else (po - pe) / (1 - pe))


def block(a, b):
    po, k = kappa(a, b)
    return {'n': len(a), 'raw_agreement': po, 'cohen_kappa': k,
            'counts_coder1': dict(collections.Counter(a)), 'counts_coder2': dict(collections.Counter(b))}


def load(p):
    d = json.loads(Path(p).read_text(encoding='utf-8'))
    assert d.get('schema') in ROUNDS, f'{p}: not a coding-tool export'
    return d['coder_id'], {r['overlap_id']: r for r in d['records'] if r.get('complete')}, d


(id1, r1, d1), (id2, r2, d2) = load(sys.argv[1]), load(sys.argv[2])
assert id1 != id2, 'the two files have the same coder ID'
assert d1['schema'] == d2['schema'], 'the two files come from different rounds'
blind_file, tag = ROUNDS[d1['schema']]
here = Path(__file__).resolve().parent
blind = {r['overlap_id']: r for r in json.loads((here / blind_file).read_text(encoding='utf-8'))}
ids = sorted(set(r1) & set(r2))
missing = sorted(set(blind) - set(ids))

out = {'round': tag, 'coders': [id1, id2], 'exported_at': [d1['exported_at'], d2['exported_at']],
       'n_records_both_complete': len(ids), 'incomplete_or_missing': missing}
s1, s2 = [r1[i]['scope'] for i in ids], [r2[i]['scope'] for i in ids]
out['scope_7class'] = block(s1, s2)
out['scope_confusion'] = {f'{x} | {y}': c for (x, y), c in sorted(collections.Counter(zip(s1, s2)).items())}
out['spatial_binary'] = block(['spatial' if s == 'station_spatial' else 'other' for s in s1],
                              ['spatial' if s == 'station_spatial' else 'other' for s in s2])
out['aspect_mention'], out['aspect_polarity_when_both_mention'] = {}, {}
for a in ASPECTS:
    m1 = ['discussed' if r1[i]['aspects'][a] != 'absent' else 'absent' for i in ids]
    m2 = ['discussed' if r2[i]['aspects'][a] != 'absent' else 'absent' for i in ids]
    out['aspect_mention'][a] = block(m1, m2)
    both = [i for i in ids if r1[i]['aspects'][a] != 'absent' and r2[i]['aspects'][a] != 'absent']
    out['aspect_polarity_when_both_mention'][a] = block([r1[i]['aspects'][a] for i in both], [r2[i]['aspects'][a] for i in both])
# pooled aspect mention (60 x 9 decisions)
p1 = [r1[i]['aspects'][a] != 'absent' for i in ids for a in ASPECTS]
p2 = [r2[i]['aspects'][a] != 'absent' for i in ids for a in ASPECTS]
out['aspect_mention_pooled'] = block(p1, p2)

(here / f'agreement_{tag}.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
with (here / f'adjudication_{tag}.csv').open('w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['overlap_id', 'station', 'text', 'any_disagreement', f'scope_{id1}', f'scope_{id2}', 'scope_adjudicated']
               + [x for a in ASPECTS for x in (f'{a}_{id1}', f'{a}_{id2}', f'{a}_adjudicated')]
               + [f'notes_{id1}', f'notes_{id2}', 'adjudication_note'])
    for i in ids:
        x, y = r1[i], r2[i]
        dis = x['scope'] != y['scope'] or any(x['aspects'][a] != y['aspects'][a] for a in ASPECTS)
        w.writerow([i, blind[i]['station'], blind[i]['text'], int(dis), x['scope'], y['scope'], '']
                   + [v for a in ASPECTS for v in (x['aspects'][a], y['aspects'][a], '')]
                   + [x.get('notes', ''), y.get('notes', ''), ''])

f3 = lambda v: 'n/a' if v is None else f'{v:.3f}'
print(f"{id1} vs {id2}: {len(ids)} records coded by both" + (f"; missing {missing}" if missing else ''))
print(f"scope (7 classes)  raw {f3(out['scope_7class']['raw_agreement'])}  kappa {f3(out['scope_7class']['cohen_kappa'])}")
print(f"spatial vs other   raw {f3(out['spatial_binary']['raw_agreement'])}  kappa {f3(out['spatial_binary']['cohen_kappa'])}")
print(f"aspect mention, pooled 9x{len(ids)}  raw {f3(out['aspect_mention_pooled']['raw_agreement'])}  kappa {f3(out['aspect_mention_pooled']['cohen_kappa'])}")
for a in ASPECTS:
    m, p = out['aspect_mention'][a], out['aspect_polarity_when_both_mention'][a]
    print(f"  {a}: mention kappa {f3(m['cohen_kappa'])} (discussed {m['counts_coder1'].get('discussed', 0)}/{m['counts_coder2'].get('discussed', 0)})"
          f" | polarity n={p['n']} raw {f3(p['raw_agreement'])}")
