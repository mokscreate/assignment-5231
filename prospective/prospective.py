"""Prospective held-out station check (Woodlands, NS9). See FREEZE.md.

python prospective.py --train            fit frozen models on the 26 other stations -> frozen_models.joblib
python prospective.py --evaluate new.json  apply them once to Woodlands reviews collected after 2026-10-04
new.json: list of {"review_id", "rating", "text", "displayed_date"} as captured; IDs already in model/data.csv are dropped.
"""
from pathlib import Path
import csv, json, sys, hashlib
import numpy as np, joblib

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent / "model"
sys.path.insert(0, str(MODEL))
from model import encode, normalize, text_input, metrics, KEYS, SEED  # noqa: E402
from polarity import code_polarity, features  # noqa: E402
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, balanced_accuracy_score, accuracy_score, roc_auc_score

STATION = "Woodlands"


def load_rows():
    return list(csv.DictReader((MODEL / "data.csv").open(encoding="utf-8-sig")))


def train():
    rows = load_rows()
    stations = sorted({r["station"] for r in rows})
    tr = [r for r in rows if r["screening_status"] == "included" and r["station"] != STATION]
    y = np.array([int(r["rating"]) >= 4 for r in tr], dtype=int)
    XB = np.array([[int(r[k]) for k in KEYS] for r in tr])
    XC = np.array([features(code_polarity(r["review_text"])) for r in tr])
    lr = lambda: LogisticRegression(C=1, class_weight="balanced", max_iter=2000, random_state=SEED)
    rf = lambda: RandomForestClassifier(n_estimators=250, max_depth=8, min_samples_leaf=10, class_weight="balanced_subsample", random_state=SEED, n_jobs=2)
    models = {"B_mention_logistic": lr().fit(XB, y), "B_mention_forest": rf().fit(XB, y),
              "C_polarity_logistic": lr().fit(XC, y), "C_polarity_forest": rf().fit(XC, y)}
    seen_ids = sorted({r["review_id"] for r in rows if r["station"] == STATION})
    train_keys = sorted({normalize(text_input(r["review_text"], stations)) for r in rows if r["review_text"].strip()})
    joblib.dump({"models": models, "stations": stations, "seen_woodlands_ids": seen_ids, "train_text_keys": train_keys,
                 "n_train": len(y), "train_stations": sorted({r["station"] for r in tr})}, HERE / "frozen_models.joblib", compress=3)
    h = hashlib.sha256((HERE / "frozen_models.joblib").read_bytes()).hexdigest()
    print(f"trained on {len(y)} records from {len({r['station'] for r in tr})} stations; Woodlands IDs already seen: {len(seen_ids)}; sha256 {h}")


def evaluate(path):
    b = joblib.load(HERE / "frozen_models.joblib")
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    seen, keys = set(b["seen_woodlands_ids"]), set(b["train_text_keys"])
    log = {"captured": len(raw), "already_in_corpus": 0, "rating_only": 0, "duplicate_text": 0, "no_spatial_match": 0, "included": 0}
    inc, own = [], set()
    for r in raw:
        if r["review_id"] in seen:
            log["already_in_corpus"] += 1; continue
        t = (r.get("text") or "").strip()
        if not t:
            log["rating_only"] += 1; continue
        k = normalize(text_input(t, b["stations"]))
        if not k or k in keys or k in own:
            log["duplicate_text"] += 1; continue
        own.add(k)
        if not any(encode(t)):
            log["no_spatial_match"] += 1; continue
        log["included"] += 1; inc.append(r)
    new_ratings = [int(r["rating"]) for r in raw if r["review_id"] not in seen]
    out = {"station": STATION, "screening": log, "new_rating_distribution": {str(s): new_ratings.count(s) for s in range(1, 6)}}
    if inc:
        y = np.array([int(r["rating"]) >= 4 for r in inc], dtype=int)
        XB = np.array([encode(r["text"]) for r in inc])
        XC = np.array([features(code_polarity(r["text"])) for r in inc])
        res, per = {}, [{"review_id": r["review_id"], "rating": int(r["rating"]), "displayed_date": r.get("displayed_date", ""),
                         "aspects": "".join(k for k, v in zip(KEYS, x) if v)} for r, x in zip(inc, XB)]
        for name, m in b["models"].items():
            p = m.predict_proba(XB if name.startswith("B") else XC)[:, 1]
            pred = (p >= .5).astype(int)
            res[name] = {"n": int(len(y)), "high": int(y.sum()), "low": int(len(y) - y.sum()), "correct": int((pred == y).sum()),
                         "accuracy": float(accuracy_score(y, pred)), "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if len(set(y)) > 1 else None,
                         "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)), "auc": float(roc_auc_score(y, p)) if len(set(y)) > 1 else None,
                         "low_correctly_flagged": int(((pred == 0) & (y == 0)).sum())}
            for d, v in zip(per, p):
                d[name] = round(float(v), 3)
        out["results"], out["per_review"] = res, per
    (HERE / "prospective_results.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_review"}, indent=1))


if __name__ == "__main__":
    if sys.argv[1:] == ["--train"]:
        train()
    elif sys.argv[1:2] == ["--evaluate"]:
        evaluate(sys.argv[2])
    else:
        print(__doc__)
