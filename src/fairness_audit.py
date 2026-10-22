import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score, brier_score_loss

processed = Path.home() / "clinical-readmission-risk" / "data" / "processed"
preds = np.load(processed / "test_predictions.npz")
y = pd.Series(preds["y_test"])
p = pd.Series(preds["p_logit"])
urban = pd.Series(preds["urban"])
wealth = pd.Series(preds["wealth"])
female = pd.Series(preds["female"])

print("Loaded: n={} prevalence={:.3f}".format(len(y), y.mean()))

def ece(y_true, y_prob, n=10):
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    e = np.quantile(y_prob, np.linspace(0, 1, n + 1))
    e[0], e[-1] = -np.inf, np.inf
    b = np.digitize(y_prob, e[1:-1])
    total = 0.0
    for i in range(n):
        m = b == i
        if m.any():
            total += m.sum() / len(y_prob) * abs(y_true[m].mean() - y_prob[m].mean())
    return float(total)

def subgroup_table(g, label):
    print("\n=== " + label + " ===")
    rows = []
    for v in sorted(g.dropna().unique()):
        m = (g == v).values
        n = int(m.sum())
        events = int(y[m].sum())
        if y[m].nunique() < 2 or n < 30:
            print("  group {}: n={:4d}  events={:3d}  (too few events for AUROC)".format(int(v), n, events))
            continue
        auroc = roc_auc_score(y[m], p[m])
        brier = brier_score_loss(y[m], p[m])
        e = ece(y[m], p[m])
        rows.append((v, n, events, auroc, brier, e))
        print("  group {}: n={:4d}  events={:3d}  auroc={:.4f}  brier={:.4f}  ece={:.4f}".format(
            int(v), n, events, auroc, brier, e))
    if rows:
        df = pd.DataFrame(rows, columns=["group", "n", "events", "auroc", "brier", "ece"]).set_index("group")
        gap = df[["auroc", "brier", "ece"]].max() - df[["auroc", "brier", "ece"]].min()
        print("  max - min:  auroc={:.4f}  brier={:.4f}  ece={:.4f}".format(
            gap["auroc"], gap["brier"], gap["ece"]))

subgroup_table(urban, "residence (0=rural, 1=urban)")
subgroup_table(wealth, "wealth quintile (1=poorest, 5=richest)")
subgroup_table(female, "sex (0=male, 1=female)")

print("\nDone.")