# Which station-space experiences go with passenger ratings? — Singapore NSL MRT

BPS5231 course project · Wang Yulu, Zhang Xinyue · National University of Singapore · November 2026

We collected accessible Google Maps rating records for the 27 North-South Line (NSL) MRT station listings and asked
(1) which station-space experiences mentioned in reviews are associated with the overall star rating,
(2) whether the most-mentioned aspects also contribute most to rating prediction, and
(3) whether recurring complaints can ground small, station-specific improvement proposals.

**One link (game first, then results; English by default, Chinese switch at top right):** https://mokscreate.github.io/assignment-5231/

**Locally:** open `index.html` in a browser. It opens the station-management game (a small demo for playing with the data) and has a button to the results page. The two pages are `game_and_site/game_en.html` / `game_zh.html` and `game_and_site/results_site.html` / `results_site_zh.html`.

## Main results

| | |
|---|---|
| Data | 21,796 ratings, 7,636 with text, 3,884 automatically selected reviews match a spatial-aspect dictionary (27 stations, collected 4 Oct 2026, newest-first) |
| Priority score (complaints x (share of those complaints rated 1-3 stars - 19.75%)) | crowding 60, cleanliness 47, wayfinding 45, amenities 37, connectivity 37, walking/transfer 36, vertical access 28, thermal comfort 22, lighting/design 8 (extra low ratings) |
| Human coding (two authors, independent, rating-blind) | Round 1 (60 reviews): scope κ 0.26, aspect-mention κ 0.47 → codebook v2 → Round 2 (40 new reviews): 0.77 / 0.67; all 100 adjudicated |
| Dictionary vs human labels (100) | station space or not: precision 0.77, recall 0.82; individual aspects: 0.49 / 0.61 |
| Station-grouped 5-fold CV (AUC) | baseline 0.48 · mention flags 0.61–0.63 · aspect + polarity 0.74 · mention + overall tone (control) 0.76 · TF-IDF text 0.80 |
| Rank stability (300 station resamples) | connectivity (C) and amenities (A) in the top three under all four B/C spatial models; vertical access (V) only in the mention-only logistic model |
| Low ratings among negative mentions | vertical access 68%, cleanliness 61% (all reviews 20%) |
| Prospective check (Woodlands, frozen pipeline) | 36 new ratings after capture, 4 entered the model, 3 of 4 classified correctly — too few to estimate performance |

The nine aspects: C station–city connectivity · M walking and transfer paths · F wayfinding and signage · V vertical circulation and accessibility · D crowding and pedestrian flow · T thermal comfort, air and shelter · Q cleanliness and maintenance · A amenities and dwell support · L lighting and spatial ambience.

## Repository layout

```
data/            reviews.csv (all 21,796 records) and station_coverage.csv (per-station collection)
model/           model.py — dictionary, screening, models, permutation importance → results.json, factor_ranking.csv, data.csv
                 polarity.py — aspect-polarity rules (option C), overall-tone control, rank stability → polarity_results.json, polarity_validation.json
                 POLARITY_SUMMARY.md — summary of the polarity and rank-stability results
annotation/      human coding
  CODEBOOK_v2.md               frozen codebook (v1 rules in review.html / annotations.json + five v2 rules)
  sample_overlap60.py, sample_round2.py      draw the round-1 (60) and round-2 (40) samples
  review_overlap60(_zh).html, review_round2_zh.html   rating-blind coding tools
  agreement_overlap60.py       Cohen's κ and raw agreement → agreement_overlap60.json, agreement_round2.json
  adjudicate.html              adjudication tool
  dictionary_vs_human.py       dictionary labels vs adjudicated labels → dictionary_vs_human.json
  human_coding/                original coder exports, NSL_adjudication_final.json, adjudication_revisions.json, PROVENANCE.md
  annotations.json, review.html, audit_summary.json   earlier 200-record single-AI development audit (not human labels)
prospective/     Woodlands prospective check: FREEZE.md (fingerprints written before collection), prospective.py,
                 frozen_models.joblib, woodlands_new.json, prospective_results.json, COLLECTION_LOG.md
game_and_site/   results_site.html / results_site_zh.html (built by make_site.py from template(_zh).html + site_data.json),
                 game_en.html / game_zh.html (built from game3_tpl(_en).html + game_data3.json)
scripts/         review collection helpers
```

## Reproduce

Python 3.12 with the packages in `model/requirements.txt`.

```bash
cd model
python model.py                 # mention-only models, importance → results.json (rewrites data.csv flags and predictions)
python polarity.py --validate   # polarity rules vs development set and human labels
python polarity.py              # options B / C / control, rank stability → polarity_results.json (~5 min)
cd ../annotation
python agreement_overlap60.py human_coding/NSL_overlap60_wang.json human_coding/NSL_overlap60_zhang.json
python agreement_overlap60.py human_coding/NSL_round2_Wang.json human_coding/NSL_round2_Zhang.json
python dictionary_vs_human.py
cd ../prospective
python prospective.py --evaluate woodlands_new.json
cd ../game_and_site
python make_site.py             # rebuilds both website versions
```

In each cross-validation fold, all reviews from a station are in training or in testing, with no overlap. Each station rotates between roles across folds.
Three seeds give two distinct station partitions. Bootstrap intervals resample fixed first-seed out-of-fold predictions.

## Data note

Reviews are public Google Maps reviews collected on 4 October 2026 (Woodlands follow-up on 16 November 2026) for course research only.
No reviewer names or profile links are stored. If you would like a review removed, please contact the authors.
The private sampling keys of the two coding rounds (`annotation/*_private_key.json`) are not published.

## Notes on interpretation

- Star ratings reflect overall evaluation, not spatial satisfaction alone; results are predictive associations, not causal effects.
- Permutation importance is the fitted model's reliance on a feature, not the benefit of changing the space; a negative or near-zero value does not mean the issue is unimportant.
- Evidence cards are review-based and labelled “review claim / needs site check”; no site visit was made.

## AI use

OpenAI tools and Claude (Anthropic) assisted with data-processing scripts, the polarity rules, the coding and adjudication tools, the website and paper drafting. All human coding was done independently by the two authors; AI annotations were used only for development and never as human labels.


## Final presentation and paper

The latest English slides, five-minute script and revised eight-page paper are in `deliverables/`. The historical 224-row pilot is preserved in `legacy/pilot_224/`.

## Frozen model

The prospective model bundle is included for direct reproduction. Its file and the pipeline hashes remain as recorded in `prospective/FREEZE.md`. The prospective script uses `joblib` in addition to the modelling dependencies.

