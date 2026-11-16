# Option C (aspect + polarity) and ranking uncertainty — summary

Script: `polarity.py` (results in `polarity_results.json`, `polarity_validation.json`).
Same 3,884 records, station-grouped 5-fold CV with 3 seeds (2 distinct partitions), same metrics as `model.py`.
Mention-only results reproduce `model.py` exactly (logistic AUC 0.609, forest 0.634).

## Polarity coder
Presence comes from the fixed dictionary in `model.py`. For each mentioned aspect, the clauses containing it are scored
with a fixed sentiment lexicon (negation within three words; requests such as "would be good if", "need", "no shelter" count as negative).
Rules never see ratings. They were checked only on the 200-record AI development set, frozen, and then tested once against the human labels.

| Reference | Aspect instances | Raw agreement | Cohen's κ | Negative recall | Positive recall |
|---|---|---|---|---|---|
| Single-AI development set (not human) | 111 | 0.748 | 0.59 | 0.86 | 0.77 |
| Human-adjudicated 100 (codebook v2), test | 54 | 0.630 | 0.34 | 0.84 | 0.25 |

Human reference counts: 37 negative, 12 positive, 4 neutral, 1 mixed. The rules find most complaints but label most praise as neutral.
This is rule-vs-human agreement, not agreement between human coders.

## Models (mean AUC / macro F1 over 3 seeds)

| Features | Logistic | Random forest |
|---|---|---|
| B: 9 mention flags | 0.609 / 0.551 | 0.634 / 0.580 |
| C: aspect × {positive, negative, neutral} | 0.739 / 0.648 | 0.739 / 0.638 |
| S (control): mention flags + whole-review sentiment counts | 0.755 / 0.669 | 0.761 / 0.680 |

Paired station-bootstrap AUC differences (first seed): C − B = +0.129 [0.089, 0.168] (logistic), +0.106 [0.077, 0.137] (forest);
C − S = −0.016 [−0.026, −0.004] (logistic), −0.022 [−0.030, −0.014] (forest).
Interpretation: adding polarity raises AUC substantially, but the gain is matched by whole-review sentiment. With this rule coder we cannot show that
knowing *which aspect* was praised or criticised adds information beyond the review's overall tone.

## Low ratings among negative vs positive mentions (rule polarity; overall 1–3★ share = 19.7%)

| Aspect | Negative mentions | of which 1–3★ | Positive mentions | of which 1–3★ |
|---|---|---|---|---|
| V vertical access | 59 | 68% | 35 | 14% |
| Q cleanliness | 114 | 61% | 535 | 6% |
| L lighting | 24 | 54% | 226 | 9% |
| M walking/transfer | 112 | 52% | 110 | 10% |
| F wayfinding | 176 | 45% | 129 | 7% |
| T thermal | 90 | 44% | 99 | 7% |
| C connectivity | 177 | 41% | 520 | 8% |
| A amenities | 201 | 38% | 630 | 9% |
| D crowding | 452 | 33% | 159 | 10% |

## Ranking uncertainty (300 station-bootstrap resamples of first-seed out-of-fold predictions; share of resamples ranked top 3)

| Aspect | B logistic | B forest | C logistic | C forest |
|---|---|---|---|---|
| C connectivity | 1.00 | 0.92 | 1.00 | 1.00 |
| V vertical access | 1.00 | 0.13 | 0.05 | 0.00 |
| A amenities | 0.92 | 1.00 | 0.95 | 1.00 |
| Q cleanliness | 0.00 | 0.95 | 1.00 | 1.00 |
| others | ≤ 0.04 | 0.00 | 0.00 | 0.00 |

C and A are in the top three under every model. V is top three only for the mention-only logistic model; Q moves from last (mention-only logistic)
to first once polarity is added, because "clean" and "dirty" carry sentiment. Rankings therefore depend on the feature set and model.
The resamples reuse fixed out-of-fold predictions; they do not refit the coding or the models.
