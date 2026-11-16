# 60-record independent human coding — provenance

- Sample: `../overlap60_blind.json`, drawn by `../sample_overlap60.py` (seed 5231060); disjoint from the 200-record AI dev set.
- Tool: `../review_overlap60_zh.html` (rating-blind; no dictionary labels or AI suggestions shown).
- Coder zhang exported 2026-11-15T10:13:03Z; coder wang exported 2026-11-15T14:24:16Z.
- Both coders coded independently before any discussion; wang confirmed (2026-11-15) that he had not seen zhang's file before finishing.
- These two JSON files are the original pre-discussion labels and are not edited. Adjudicated labels live separately in `../adjudication_overlap60.csv`.
- Agreement statistics: `../agreement_overlap60.json` (produced by `../agreement_overlap60.py`).

## Round 2 (40 records, codebook v2)
- Sample: `../round2_blind.json` (`../sample_round2.py`, seed 5231040); disjoint from the 200 dev records and the 60 round-1 records.
- Tool: `../review_round2_zh.html`, with a literal Chinese reading aid under each English text (AI-written by Claude, `../round2_translations_zh.json`; the English original is the coded text).
- The translation was added on 2026-11-16 before either coder started round 2, so both coders used the same version.
- On 2026-11-16 (before Zhang started round 2) the tool was changed so that choosing a scope pre-fills every still-blank aspect with `absent`; coders then change the aspects that are discussed. Each exported record lists the pre-filled aspects in `prefilled_absent`. Round 1 had no pre-fill.
- Round-2 exports: Wang coded 2026-11-16T05:57–06:55Z and exported 06:55:34Z; Zhang coded 06:55:52–07:00:38Z and exported 07:00:44Z. Independence confirmation for round 2: pending.
- Round-2 agreement: `../agreement_round2.json`; adjudication sheet `../adjudication_round2.csv`.
- Round 2 independence: Wang confirmed on 2026-11-16 that both coders coded round 2 independently.

## Adjudication
- `NSL_adjudication.json`: adjudicated labels for all 100 records (60 + 40) exported from `../adjudicate.html` (2026-11-16), decided by Wang and Zhang under codebook v2.
- `NSL_adjudication_final.json`: final adjudicated labels. 11 records were revised afterwards by Wang to apply v2 consistently (some were labels both coders had agreed on and so were not shown in the adjudication page); each change and reason is in `adjudication_revisions.json`.
- Agreement statistics always use the original coder files, never adjudicated labels.
