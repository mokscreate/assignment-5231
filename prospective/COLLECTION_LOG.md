# Collection and evaluation log — Woodlands prospective check

- 2026-11-16 ~17:31 (SGT): FREEZE.md, prospective.py and frozen_models.joblib written and copied to NSL_Work before any new review was loaded.
- ~17:33: Google Maps (Woodlands MRT listing, English UI) showed 465 reviews vs 432 in the corpus. Sorting and loading more than 5 reviews required a Google sign-in; Wang Yulu signed in himself in the built-in browser (no credentials handled by Claude).
- ~17:36: Sorted by Newest and loaded the first 120 reviews (back to "4 months ago"). New reviews were identified by review ID against the 432 Woodlands IDs in model/data.csv. The first 36 reviews were new and every later review was already in the corpus, so the stopping rule in FREEZE.md was met.
- The collector (Claude) saw the new texts while extracting them. Nothing in the frozen files was changed afterwards: sha256 of prospective.py and frozen_models.joblib at evaluation time match FREEZE.md.
- Evaluation was run once: `python prospective.py --evaluate woodlands_new.json` -> prospective_results.json.

Result: 36 new ratings (27 five-star, 5 four-star, 4 three-star, none 1–2); 26 rating-only, 2 duplicate texts, 4 with no spatial aspect,
4 included in the model. All 4 included reviews are 4–5 stars, so AUC and balanced accuracy are undefined; each frozen model classified
3 of 4 correctly. The check confirms the frozen pipeline runs end to end on new reviews; the sample is too small to estimate performance.
