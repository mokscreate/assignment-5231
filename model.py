"""Core NSL pilot: repeated validation and held-out permutation importance."""
import csv
import json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parent
FEATURES = {
    "C": "Station-city connectivity",
    "M": "Horizontal circulation and transfer paths",
    "F": "Wayfinding and signage",
    "V": "Vertical circulation and accessibility",
    "D": "Crowding and pedestrian flow",
    "T": "Thermal comfort, air and shelter",
    "Q": "Cleanliness and facility maintenance",
    "A": "Amenities and dwell support",
    "L": "Lighting and spatial ambience",
}

def main():
    with (ROOT / "data.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    keys = list(FEATURES)
    X = np.array([[int(r[k]) for k in keys] for r in rows], dtype=float)
    y = np.array([int(r["stars"]) >= 4 for r in rows], dtype=int)
    assert set(np.unique(X)) <= {0, 1}, "Features must be binary mention flags"
    assert np.bincount(y).min() >= 5, "Each class needs at least five records"
    metrics, importances = [], []
    for repeat in range(10):
        cv = StratifiedKFold(5, shuffle=True, random_state=5231 + repeat)
        predicted = np.zeros(len(y), dtype=int)
        probability = np.zeros(len(y))
        baseline_pred = np.zeros(len(y), dtype=int)
        baseline_prob = np.zeros(len(y))
        fold_importance = []
        for fold, (train, test) in enumerate(cv.split(X, y)):
            model = LogisticRegression(C=1.0, class_weight="balanced",
                                       max_iter=2000, solver="lbfgs")
            model.fit(X[train], y[train])
            baseline = DummyClassifier(strategy="prior").fit(X[train], y[train])
            predicted[test] = model.predict(X[test])
            probability[test] = model.predict_proba(X[test])[:, 1]
            baseline_pred[test] = baseline.predict(X[test])
            baseline_prob[test] = baseline.predict_proba(X[test])[:, 1]
            importance = permutation_importance(
                model, X[test], y[test], scoring="roc_auc", n_repeats=20,
                random_state=900 + repeat * 5 + fold)
            fold_importance.append(importance.importances_mean)
        importances.append(np.mean(fold_importance, axis=0))
        for name, pred, prob in [("LogisticRegression", predicted, probability),
                                 ("MajorityBaseline", baseline_pred, baseline_prob)]:
            metrics.append({"repeat": repeat, "model": name,
                "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
                "accuracy": float(accuracy_score(y, pred)),
                "auc": float(roc_auc_score(y, prob))})
    mean_importance = np.mean(importances, axis=0)
    importance_ranks = np.argsort(np.argsort(-mean_importance)) + 1
    counts = X.sum(axis=0).astype(int)
    frequency_ranks = np.argsort(np.argsort(-counts)) + 1
    factors = [{"feature": k, "name": FEATURES[k], "mentions": int(counts[j]),
                "frequency_rank": int(frequency_ranks[j]),
                "importance_rank": int(importance_ranks[j]),
                "test_auc_drop": float(mean_importance[j])}
               for j, k in enumerate(keys)]
    summary = {"n": len(rows), "high_rating_n": int(y.sum()),
        "performance": {name: {key: float(np.mean([m[key] for m in metrics
                          if m["model"] == name]))
                          for key in ["macro_f1", "accuracy", "auc"]}
                        for name in ["LogisticRegression", "MajorityBaseline"]},
        "factors": sorted(factors, key=lambda f: f["importance_rank"])}
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (output / "factor_ranking.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(factors[0]))
        writer.writeheader()
        writer.writerows(summary["factors"])
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
