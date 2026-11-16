# Prospective held-out station check — freeze record

Written 2026-11-16 (Singapore time), before any new review was collected or read.

## Station
**Woodlands (NS9).** Rule fixed in advance: the station with the most reviews dated within one month before the 2026-10-04 capture
(54 ratings, 18 with text), excluding the three case-card stations. Woodlands' 432 historical records were seen during
development and auditing; this is a prospective check on newly posted reviews, not a station never seen in development.

## What is frozen (sha256)
| File | sha256 |
|---|---|
| model/model.py (dictionary, screening, model settings) | a13697c24cd2996c00aea764a59b97716b3a51659809c8249c38cee11031cc9f |
| model/polarity.py (polarity rules) | 86f1bc1f74ae794fb1c77ac81b6e1c6739b176bad0688ce848d68313d7fa20f8 |
| annotation/CODEBOOK_v2.md | 9ac56e3dec96e5f479548a1b412c1b6dbae06e053c183ba3ccfa7b3c80e17f98 |
| model/data.csv (training corpus) | 9b5efbe810b5806736bb381961ab263a35ccca9f74effe5d505e789b0274103d |
| prospective/prospective.py (this procedure) | 39ce3408fabec69612426d5f888b6b90931b10c3d7f0cc8a452138ee6fdf2713 |
| prospective/frozen_models.joblib | ff29168ae1a1f9c6c98759bdc2794430848a40675bca12a6b702d9cb6f7676e6 |

## Models
Fitted once on the 3,789 included records of the other 26 stations (all Woodlands records excluded), with the same settings as
`model.py` / `polarity.py`: B mention flags (logistic, random forest) and C aspect + polarity (logistic, random forest).
**Primary model: B mention logistic** (the paper's main spatial model). The others are reported alongside.

## New data
Collect Woodlands reviews from Google Maps sorted newest-first, stopping at the first review that is already in the corpus.
A review counts as new if its review ID is not among the 432 Woodlands IDs in `model/data.csv`. No review text is used to change
anything above. Screening is the same as `model.py`: text present, not a duplicate of any corpus text, at least one dictionary aspect.

## Evaluation (run once)
`python prospective.py --evaluate woodlands_new.json`. Report: screening counts, rating distribution, and for each model the number of
included reviews, high/low counts, correct predictions, accuracy, macro F1, and balanced accuracy and AUC when both classes are present,
plus per-review predictions. With an expected 10–25 included reviews these figures are reported as counts, not as a stable estimate.
No threshold, feature, rule or model is changed after the evaluation.
