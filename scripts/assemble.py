"""Assemble browser-observed reviews. No generated or inferred review text."""
from pathlib import Path
import csv, json, re, zipfile

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent
OUT = ROOT / 'output' / 'NSL_Review_Data'
OUT.mkdir(parents=True, exist_ok=True)
index = json.loads((ROOT/'tmp/nsl100/NSL_station_counts.json').read_text(encoding='utf-8-sig'))['reviews']
index.sort(key=lambda x: int(x['code'][2:]))
records, coverage, seen = [], [], set()
for station in index:
    path = RAW / (station['station'].replace(' ', '_')+'.json')
    obj = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    unique = {}
    for r in obj.get('reviews', []):
        assert r.get('review_id'), (station['station'], 'Missing review ID')
        unique[r['review_id']] = r
    text_count = 0
    for rid, r in unique.items():
        key = (station['code'], rid)
        assert key not in seen
        seen.add(key)
        rating = int(re.match(r'[1-5]', r['stars'])[0])
        text = r.get('text', '').strip()
        text_count += bool(text)
        records.append(dict(station_code=station['code'], station=station['station'],
            review_id=rid, rating=rating, displayed_date=r.get('displayed_date',''),
            review_text=text, has_text=int(bool(text)), displayed_language=r.get('language',''),
            collected_date=obj.get('collected_date',''), source_url=obj.get('source_url',station['url']),
            spatial_coding_status='not_coded', possible_truncation=int(text.endswith(('…','...')))))
    total = obj.get('displayed_total',station['count'])
    n = len(unique)
    status = 'count_matched' if n == total else ('list_exhausted_count_gap' if station['station']=='Yew Tee' and n==145 and total==146 else 'incomplete')
    coverage.append(dict(station_code=station['code'],station=station['station'],
        displayed_total=total,collected_records=n,text_records=text_count,
        rating_only_records=n-text_count,uncollected_count=max(0,total-n),
        collection_status=status,source_url=obj.get('source_url',station['url'])))

def write_csv(name, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

write_csv('reviews.csv',records)
write_csv('station_coverage.csv',coverage)
text_n=sum(r['has_text'] for r in records)
matched=sum(s['collection_status']=='count_matched' for s in coverage)
total=sum(s['displayed_total'] for s in coverage)
readme=f'''NSL MRT review collection — 4 October 2026

STATUS: Accessible review-list collection completed. One listing has a one-record count gap; this is not a claim of a complete historical census.

27 NSL station listings covered.
{len(records):,} unique station/review records saved.
{text_n:,} records contain text; {len(records)-text_n:,} contain only a rating.
{matched} station counts match the displayed Google Maps total.
The station listings display {total:,} ratings/reviews in total. This is NOT the number of usable text reviews.

FILES
reviews.csv: observed ratings, displayed review text, relative dates, station and source.
station_coverage.csv: per-station collection totals and remaining gaps.

METHOD
Open the canonical MRT/LRT station listing, select Reviews and Newest, scroll the review list and expand See more. Save only data visible in the page DOM. Deduplicate by station and Google review ID. No reviewer names or profile links are included. No synthetic reviews are included. Small numbers of initial relevance-sorted cards may have been observed while the sort changed; this is not a random sample.

INTERPRETATION
Text records are not yet validated spatial-experience samples. They include generic comments, operational issues, comments about nearby businesses, multilingual text and possible off-topic content. Ratings-only records are retained for transparent accounting but cannot provide text-derived spatial features.
Some displayed English text is Google's automatic translation. displayed_language is a DOM language tag, not verified original language. Relative dates are preserved as displayed; they are not precise publication dates. possible_truncation is only an end-of-text flag, not a completeness guarantee.
Interchange-station comments may discuss other lines. The unit is the station listing, not an exclusively NSL train experience.
A matched count means the saved unique count matches the listing total at collection. It is not proof that Google exposes every historical review. Counts may change over time. Yew Tee stopped at 145 while the listing displayed 146, including after a second navigation and full list expansion. That missing record has not been fabricated or inferred.
Jurong East was extracted in 500-record chunks and merged by review ID to avoid per-read size limits. Longer observed versions of a review were retained when merging repeated captures.

NEXT ANALYSIS
Screen station relevance; separate spatial, operational and generic content. Develop and validate aspect labels before training. Compare mention frequency with held-out predictive importance. Keep ratings out of feature annotation. Use station-grouped validation and uncertainty estimates. The former 224-row pilot and its model scores must not be presented as results for this expanded corpus.
This package contains raw research observations, not new model results or causal evidence.
'''
(OUT/'README.txt').write_text(readme,encoding='utf-8')
with zipfile.ZipFile(ROOT/'output/NSL_Review_Data.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['reviews.csv','station_coverage.csv','README.txt']:z.write(OUT/name,name)
print(json.dumps(dict(stations=len(coverage),records=len(records),text_records=text_n,count_matched=matched,displayed_total=total),indent=2))
