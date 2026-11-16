"""Draw the 40-record round-2 coding set (two independent coders, frozen codebook).
Same pool and rules as sample_overlap60.py; also excludes the 60 round-1 records.

Pool: model/data.csv text records, normalised-text dedup, excluding every record
in the 200-record AI dev set (annotations.json). English, 3-150 words.
Strata (disproportionate, diagnostic; not population prevalence):
  (round 2 quotas: rare 8, boundary 6, hit 12, miss_cue 5, miss 9)
  rare      12  dictionary hits on the rarer aspects V/T/L/F/M (>=2 each)
  boundary   8  short dictionary hits only on C, L or A (weak boundaries found in the audit)
  hit       18  other dictionary hits
  miss_cue   8  no dictionary hit but a station-space cue word (possible misses)
  miss      14  no dictionary hit
Within each stratum: round-robin over rating band (1-2 / 3 / 4-5) and station.
Ratings are used only for coverage and are hidden from coders.
Outputs: round2_blind.json (public), round2_private_key.json (gitignored).
"""
from pathlib import Path
import csv, json, random, re, collections

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SEED = 5231040
ASPECTS = 'CMFVDTQAL'
CUE = re.compile(r'\b(station|mrt|platform|exit|entrance|interchange|bus|mall|walk|stairs?|door|gantry|underground|concourse|overhead|bridge|corridor)\b', re.I)
RATING_PHRASE = re.compile(r'\b(?:[1-5]|one|two|three|four|five)\s*(?:out of\s*(?:5|five)|/5|[- ]?stars?)\b|\b[0-5]\s*\*|\bstars?\b', re.I)

rows = list(csv.DictReader((REPO / 'model/data.csv').open(encoding='utf-8-sig')))
dev = {a['review_id'] for a in json.loads((HERE / 'annotations.json').read_text(encoding='utf-8'))}
dev |= {a['review_id'] for a in json.loads((HERE / 'overlap60_blind.json').read_text(encoding='utf-8'))}
seen, pool = set(), []
for r in rows:
    t = r['review_text'].strip()
    k = re.sub(r'[^\w]+', ' ', t.casefold()).strip()
    if not k or k in seen:
        continue
    seen.add(k)
    if r['review_id'] in dev or r['displayed_language'] not in ('en', ''):
        continue
    if not 3 <= len(t.split()) <= 150 or RATING_PHRASE.search(t):
        continue  # skip texts that reveal the rating rather than masking them
    r['_hits'] = [a for a in ASPECTS if r[a] == '1']
    r['_band'] = 'low' if int(r['rating']) <= 2 else 'neutral' if int(r['rating']) == 3 else 'high'
    pool.append(r)

rng = random.Random(SEED)
rng.shuffle(pool)
taken = set()

def draw(cands, n, label):
    groups = collections.defaultdict(list)
    for r in cands:
        if r['review_id'] not in taken:
            groups[r['_band']].append(r)
    out, used_st = [], collections.Counter()
    while len(out) < n and any(groups.values()):
        for b in ('low', 'neutral', 'high'):
            g = groups[b]
            if not g or len(out) == n:
                continue
            g.sort(key=lambda r: used_st[r['station']])  # spread stations
            r = g.pop(0)
            if r['review_id'] in taken:
                continue
            taken.add(r['review_id']); used_st[r['station']] += 1
            r['_stratum'] = label; out.append(r)
    return out

sample = []
for a, k in zip('VTLFM', (2, 2, 1, 2, 1)):  # rare aspects -> 8
    sample += draw([r for r in pool if a in r['_hits']], k, f'rare_{a}')
sample += draw([r for r in pool if len(r['_hits']) == 1 and r['_hits'][0] in 'CLA' and len(r['review_text'].split()) <= 15], 6, 'boundary')
sample += draw([r for r in pool if r['_hits']], 12, 'hit')
sample += draw([r for r in pool if not r['_hits'] and CUE.search(r['review_text'])], 5, 'miss_cue')
sample += draw([r for r in pool if not r['_hits']], 9, 'miss')
assert len(sample) == 40, len(sample)
rng.shuffle(sample)

blind, private = [], []
for i, r in enumerate(sample, 1):
    ident = f'S{i:02}'
    blind.append({'overlap_id': ident, 'station': r['station'], 'review_id': r['review_id'], 'text': r['review_text'].strip()})
    private.append({'overlap_id': ident, 'review_id': r['review_id'], 'station': r['station'], 'rating': int(r['rating']),
                    'band': r['_band'], 'stratum': r['_stratum'], 'dictionary_hits': ''.join(r['_hits']),
                    'displayed_date': r['displayed_date'], 'source_url': r['source_url'], 'text': r['review_text'].strip()})
(HERE / 'round2_blind.json').write_text(json.dumps(blind, ensure_ascii=False, indent=1), encoding='utf-8')
(HERE / 'round2_private_key.json').write_text(json.dumps(private, ensure_ascii=False, indent=1), encoding='utf-8')
c = collections.Counter
print('pool', len(pool), '| stations', len({r['station'] for r in sample}))
print('strata', c(r['_stratum'].split('_')[0] for r in sample))
print('bands', c(r['_band'] for r in sample), '| dictionary hit', sum(bool(r['_hits']) for r in sample))
print('aspect hits', {a: sum(a in r['_hits'] for r in sample) for a in ASPECTS})
