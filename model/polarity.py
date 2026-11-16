"""Aspect-plus-polarity features (option C) and ranking uncertainty.

Rule-based: for each aspect the fixed dictionary in model.py finds, the clauses that
mention it are scored with a small fixed sentiment lexicon (with negation).
The rules never see ratings. They were checked only against the 200-record AI
development set (annotation/annotations.json) and are then evaluated once against
the 100 human-adjudicated records (annotation/human_coding/NSL_adjudication_final.json).

Run: python polarity.py            -> polarity_results.json, polarity_validation.json
Uses the same included records, station-grouped folds (3 seeds x 5) and metrics as model.py.
"""
from pathlib import Path
import csv, json, re, sys
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from model import ASPECTS, RULES, KEYS, SEED, normalize, text_input, metrics, ci  # noqa: E402

POS = r"good|great|nice|clean|cleaner|convenient|conveniently|easy|easily|clear|clearly|excellent|love|loved|lovely|comfortable|comfy|spacious|beautiful|well|efficient|helpful|best|awesome|amazing|pleasant|fast|quick|smooth|cool|cooling|bright|modern|neat|tidy|organised|organized|accessible|friendly|wonderful|fantastic|perfect|enjoy|enjoyable|recommend|wide|safe|fresh|airy|cosy|cozy|okay|ok|decent|fine|sufficient|ample|happy|impressive|好|方便|干净|整洁|舒适|宽敞|清楚|便利|不错|漂亮|凉快"
NEG = r"too|hate|hated|heat|frustrated|frustrating|tricky|need|needs|needed|should|hopefully|please|pls|wish|bad|poor|poorly|terrible|dirty|filthy|confusing|confused|confuse|lost|crowded|crowd|packed|congested|congestion|cramped|hot|stuffy|warm|humid|smelly|smell|smells|stink|stinks|stinky|broken|slow|far|long|worst|awful|horrible|inconvenient|difficult|hard|lack|lacking|lacks|insufficient|limited|narrow|dark|dim|leak|leaking|ugly|old|outdated|messy|rude|unclear|misleading|annoying|frustrating|nightmare|chaos|chaotic|mess|disgusting|unhygienic|tiring|tired|wet|slippery|dangerous|noisy|loud|queue|queues|queuing|jam|jammed|stuck|closed|locked|missing|few|zero|不好|脏|臭|挤|拥挤|乱|热|闷|远|难找|迷路|不方便|坏"
NEGATE = r"not|no|never|isn't|isnt|wasn't|wasnt|aren't|arent|don't|dont|doesn't|doesnt|didn't|didnt|hardly|barely|without|nor|cannot|can't|cant|less|不|没|没有|无"
POS_RE, NEG_RE, NEGATE_RE = (re.compile(rf"(?:{p})", re.I) for p in (POS, NEG, NEGATE))
TOKEN = re.compile(r"[a-z']+|[一-鿿]+", re.I)
SPLIT = re.compile(r"[.!?;\n。！？；]+|\bbut\b|\bhowever\b|\balthough\b|\bthough\b|\bexcept\b|但是|但|不过", re.I)


REQUEST = re.compile(r"\b(?:would|will) be (?:good|nice|great|better) if\b|\bcould (?:do with|use)\b|\bunder maint\w*", re.I)


def clause_score(clause, aspect=None):
    clause = REQUEST.sub(" lack ", clause)
    toks = TOKEN.findall(clause.lower())
    score = 0
    for i, t in enumerate(toks):
        p = 1 if POS_RE.fullmatch(t) else -1 if NEG_RE.fullmatch(t) else 0
        if not p:
            continue
        if any(NEGATE_RE.fullmatch(w) for w in toks[max(0, i - 3):i]):
            p = -p
        score += p
    if aspect is not None:  # "no shelter", "without lifts": negator right before the aspect word
        m = re.search(rf"\b(?:no|without|lack of|lacking|not enough|insufficient)\s+(?:\w+\s+)?(?:{ASPECTS[aspect][1]})", clause, re.I)
        if m:
            score -= 1
    return score


def code_polarity(text):
    """Return {aspect: absent|positive|negative|neutral|mixed} using the model.py dictionary for presence."""
    clauses = [c for c in SPLIT.split(text) if c and c.strip()]
    out = {}
    for k in KEYS:
        if not RULES[k].search(text):
            out[k] = "absent"
            continue
        sc = [clause_score(c, k) for c in clauses if RULES[k].search(c)]
        if not sc:  # keyword spans a split boundary
            sc = [clause_score(text, k)]
        pos, neg = any(s > 0 for s in sc), any(s < 0 for s in sc)
        out[k] = "mixed" if pos and neg else "positive" if pos else "negative" if neg else "neutral"
    return out


def features(pol):
    """Option C: per aspect, positive / negative / neutral indicators (mixed sets positive and negative)."""
    row = []
    for k in KEYS:
        v = pol[k]
        row += [int(v in ("positive", "mixed")), int(v in ("negative", "mixed")), int(v == "neutral")]
    return row


def kappa(a, b):
    n = len(a)
    if not n:
        return None, None
    po = sum(x == y for x, y in zip(a, b)) / n
    labs = set(a) | set(b)
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labs)
    return po, (None if pe == 1 else (po - pe) / (1 - pe))


def agreement(records, ref_label):
    """Compare rule polarity to a reference on aspect instances where both say the aspect is discussed."""
    pairs, mention = [], {k: [0, 0, 0, 0] for k in KEYS}  # tp fp fn tn for presence
    for text, ref in records:
        sys_pol = code_polarity(text)
        for k in KEYS:
            r, s = ref[k], sys_pol[k]
            rd, sd = r != "absent", s != "absent"
            mention[k][0 if rd and sd else 1 if sd else 2 if rd else 3] += 1
            if rd and sd and r != "uncertain":
                pairs.append((k, r, s))
    ref_l, sys_l = [p[1] for p in pairs], [p[2] for p in pairs]
    po, kp = kappa(ref_l, sys_l)
    conf = {}
    for _, r, s in pairs:
        conf[f"{r} | {s}"] = conf.get(f"{r} | {s}", 0) + 1
    neg_ref = [p for p in pairs if p[1] == "negative"]
    pos_ref = [p for p in pairs if p[1] == "positive"]
    return {"aspect_instances_compared": len(pairs), "raw_agreement": po, "cohen_kappa": kp,
            "reference_counts": {l: ref_l.count(l) for l in sorted(set(ref_l))},
            "rule_counts": {l: sys_l.count(l) for l in sorted(set(sys_l))},
            "confusion_reference_by_rule": conf,
            "negative_recall": (sum(p[2] in ("negative", "mixed") for p in neg_ref) / len(neg_ref)) if neg_ref else None,
            "positive_recall": (sum(p[2] in ("positive", "mixed") for p in pos_ref) / len(pos_ref)) if pos_ref else None,
            "presence_dictionary_vs_reference": {k: dict(zip(["both", "dictionary_only", "reference_only", "neither"], v)) for k, v in mention.items()},
            "note": "Uncertain reference labels excluded. Presence comes from the fixed dictionary, polarity from the rule lexicon."}


def validate(dev_only=False):
    ann = ROOT.parent / "annotation"
    dev = json.loads((ann / "annotations.json").read_text(encoding="utf-8"))
    dev_records = [(d["review_text_blinded"], d["aspects_ai"]) for d in dev if d["scope_ai"] == "station_spatial"]
    blind = {r["overlap_id"]: r["text"] for f in ("overlap60_blind.json", "round2_blind.json")
             for r in json.loads((ann / f).read_text(encoding="utf-8"))}
    final = json.loads((ann / "human_coding" / "NSL_adjudication_final.json").read_text(encoding="utf-8"))
    hum_records = [(blind[r["overlap_id"]], r["aspects"]) for rs in final["rounds"].values() for r in rs if r["scope"] == "station_spatial"]
    out = {"development_vs_single_AI_200": {**agreement(dev_records, "ai"), "records": len(dev_records),
                                            "reference": "single-AI initial annotation (development only, not human)"}}
    if not dev_only:
        out["test_vs_human_adjudicated_100"] = {**agreement(hum_records, "human"), "records": len(hum_records),
                                                "reference": "human adjudicated labels, codebook v2 (station_spatial records only)"}
    return out


def main():
    rows = [r for r in csv.DictReader((ROOT / "data.csv").open(encoding="utf-8-sig")) if r["screening_status"] == "included"]
    stations = sorted({r["station"] for r in csv.DictReader((ROOT / "data.csv").open(encoding="utf-8-sig"))})
    XB = np.array([[int(r[k]) for k in KEYS] for r in rows])
    pols = [code_polarity(r["review_text"]) for r in rows]
    XC = np.array([features(p) for p in pols])
    # control: whole-review sentiment, ignoring aspects (sign of each clause, counted)
    def overall(t):
        sc = [clause_score(c) for c in SPLIT.split(t) if c and c.strip()]
        return [sum(x > 0 for x in sc), sum(x < 0 for x in sc), int(sum(sc) > 0), int(sum(sc) < 0)]
    XS = np.hstack([XB, np.array([overall(r["review_text"]) for r in rows])])
    y = np.array([int(r["rating"]) >= 4 for r in rows], dtype=int)
    groups = np.array([r["station"] for r in rows])
    assert len(y) == 3884
    lr = lambda: LogisticRegression(C=1, class_weight="balanced", max_iter=2000, random_state=SEED)
    rf = lambda: RandomForestClassifier(n_estimators=250, max_depth=8, min_samples_leaf=10, class_weight="balanced_subsample", random_state=SEED, n_jobs=2)
    models = {"B_mention_logistic": (lr, XB), "B_mention_forest": (rf, XB), "C_polarity_logistic": (lr, XC), "C_polarity_forest": (rf, XC),
              "S_mention_plus_overall_sentiment_logistic": (lr, XS), "S_mention_plus_overall_sentiment_forest": (rf, XS)}
    # column groups per aspect for permutation importance
    cols = {"B": {k: [i] for i, k in enumerate(KEYS)}, "C": {k: [3 * i, 3 * i + 1, 3 * i + 2] for i, k in enumerate(KEYS)}, "S": {k: [i] for i, k in enumerate(KEYS)}}
    oof = {n: np.zeros((3, len(y))) for n in models}
    shuffled = {n: np.zeros((6, len(y), len(KEYS))) for n in models}
    for repeat in range(3):
        for fold, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=SEED + repeat).split(XB, y, groups)):
            assert not (set(groups[tr]) & set(groups[te]))
            for n, (ctor, X) in models.items():
                m = ctor().fit(X[tr], y[tr])
                oof[n][repeat, te] = m.predict_proba(X[te])[:, 1]
                if repeat == 0:
                    rng = np.random.default_rng(SEED + fold)
                    for a, k in enumerate(KEYS):
                        cg = cols[n[0]][k]
                        for perm in range(6):
                            xp = X[te].copy()
                            for s in np.unique(groups[te]):
                                ix = np.flatnonzero(groups[te] == s)
                                xp[ix[:, None], cg] = xp[rng.permutation(ix)][:, cg]
                            shuffled[n][perm, te, a] = m.predict_proba(xp)[:, 1]
        print(f"repeat {repeat + 1}/3 done", flush=True)
    rng = np.random.default_rng(SEED)
    gs = np.unique(groups)
    boot = [np.concatenate([np.flatnonzero(groups == s) for s in rng.choice(gs, len(gs), replace=True)]) for _ in range(300)]
    perf, imp = {}, {}
    for n, p in oof.items():
        per = [metrics(y, v) for v in p]
        draws = [metrics(y[ix], p[0, ix]) for ix in boot]
        perf[n] = {"mean_repeated_group_cv": {k: float(np.mean([m[k] for m in per])) for k in per[0]},
                   "first_repeat_station_bootstrap_95_ci": {k: ci([d[k] for d in draws]) for k in per[0]}}
        base = roc_auc_score(y, p[0])
        drops = {k: base - np.mean([roc_auc_score(y, shuffled[n][j, :, a]) for j in range(6)]) for a, k in enumerate(KEYS)}
        bd = np.array([[roc_auc_score(y[ix], p[0, ix]) - np.mean([roc_auc_score(y[ix], shuffled[n][j, ix, a]) for j in range(6)])
                        for a in range(len(KEYS))] for ix in boot])
        ranks = (-bd).argsort(axis=1).argsort(axis=1) + 1  # 1 = largest drop in that draw
        imp[n] = {k: {"auc_drop": float(drops[k]), "ci": ci(bd[:, a]), "rank": int(1 + sum(drops[j] > drops[k] for j in KEYS)),
                      "bootstrap_rank_median": float(np.median(ranks[:, a])), "bootstrap_rank_95": [int(x) for x in np.percentile(ranks[:, a], [2.5, 97.5])],
                      "share_top3": float(np.mean(ranks[:, a] <= 3))} for a, k in enumerate(KEYS)}
    # paired C - B difference on the same station resamples (first repeat)
    paired = {}
    for fam in ("logistic", "forest"):
        for hi, lo, lab in (("C_polarity", "B_mention", "C_minus_B"), ("C_polarity", "S_mention_plus_overall_sentiment", "C_minus_S"), ("S_mention_plus_overall_sentiment", "B_mention", "S_minus_B")):
            c, b = oof[f"{hi}_{fam}"][0], oof[f"{lo}_{fam}"][0]
            d = [roc_auc_score(y[ix], c[ix]) - roc_auc_score(y[ix], b[ix]) for ix in boot]
            paired[f"{fam}_{lab}"] = {"auc_difference": float(roc_auc_score(y, c) - roc_auc_score(y, b)), "station_bootstrap_95_ci": ci(d),
                                      "mean_over_3_repeats": float(np.mean([roc_auc_score(y, oof[f"{hi}_{fam}"][r]) - roc_auc_score(y, oof[f"{lo}_{fam}"][r]) for r in range(3)]))}
    dist = {k: {v: sum(p[k] == v for p in pols) for v in ("positive", "negative", "neutral", "mixed")} for k in KEYS}
    low = {k: {v: int(sum((p[k] == v) and yy == 0 for p, yy in zip(pols, y))) for v in ("positive", "negative", "neutral", "mixed")} for k in KEYS}
    out = {"scope": "Option C: rule-based aspect polarity on the same 3,884 records and station-grouped folds as model.py (3 seeds x 5 folds; 2 distinct partitions). Rules never see ratings.",
           "performance": perf, "paired_auc_difference": paired, "importance_and_rank_uncertainty": imp,
           "polarity_counts": dist, "polarity_counts_rated_1_3": low,
           "check_reproduces_model_py": {"B_mention_logistic_auc": perf["B_mention_logistic"]["mean_repeated_group_cv"]["auc"],
                                         "B_mention_forest_auc": perf["B_mention_forest"]["mean_repeated_group_cv"]["auc"]}}
    (ROOT / "polarity_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({n: {k: round(v, 3) for k, v in perf[n]["mean_repeated_group_cv"].items()} for n in perf}, indent=1))
    print(json.dumps(paired, indent=1))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--validate"]:
        v = validate(dev_only=sys.argv[2:] == ["--dev"])
        if sys.argv[2:] != ["--dev"]:
            (ROOT / "polarity_validation.json").write_text(json.dumps(v, indent=2), encoding="utf-8")
        for k, r in v.items():
            print(k, "| n", r["aspect_instances_compared"], "| raw", round(r["raw_agreement"], 3), "| kappa", None if r["cohen_kappa"] is None else round(r["cohen_kappa"], 3),
                  "| neg recall", None if r["negative_recall"] is None else round(r["negative_recall"], 2), "| pos recall", None if r["positive_recall"] is None else round(r["positive_recall"], 2))
            print("  ref", r["reference_counts"], "rule", r["rule_counts"])
    else:
        main()
