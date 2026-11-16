"""Check the automatic dictionary labels used by the model against the 100 human-adjudicated records.

Run: python dictionary_vs_human.py  -> dictionary_vs_human.json
Scope: dictionary 'any aspect found' vs human scope == station_spatial.
Aspects: dictionary flag vs human label != absent, per aspect and pooled (9 x 100 decisions).
"""
from pathlib import Path
import json, sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "model"))
from model import encode, KEYS  # noqa: E402

blind = {r["overlap_id"]: r["text"] for f in ("overlap60_blind.json", "round2_blind.json")
         for r in json.loads((HERE / f).read_text(encoding="utf-8"))}
final = [r for rs in json.loads((HERE / "human_coding" / "NSL_adjudication_final.json").read_text(encoding="utf-8"))["rounds"].values() for r in rs]


def summarise(pairs):
    tp = sum(d and h for d, h in pairs); fp = sum(d and not h for d, h in pairs)
    fn = sum(h and not d for d, h in pairs); tn = sum(not d and not h for d, h in pairs)
    n = len(pairs); po = (tp + tn) / n
    pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / n / n
    return {"n": n, "both": tp, "dictionary_only": fp, "human_only": fn, "neither": tn,
            "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None,
            "raw_agreement": po, "cohen_kappa": None if pe == 1 else (po - pe) / (1 - pe)}


scope, asp = [], {k: [] for k in KEYS}
for r in final:
    flags = encode(blind[r["overlap_id"]])
    scope.append((any(flags), r["scope"] == "station_spatial"))
    for k, v in zip(KEYS, flags):
        asp[k].append((bool(v), r["aspects"][k] != "absent"))
out = {"reference": "human adjudicated labels, codebook v2, 100 records (60 round 1 + 40 round 2)",
       "scope_station_spatial": summarise(scope),
       "aspect_mention_pooled": summarise([p for k in KEYS for p in asp[k]]),
       "aspect_mention": {k: summarise(v) for k, v in asp.items()}}
(HERE / "dictionary_vs_human.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
for k in ("scope_station_spatial", "aspect_mention_pooled"):
    v = out[k]; print(k, {x: (round(y, 3) if isinstance(y, float) else y) for x, y in v.items()})
