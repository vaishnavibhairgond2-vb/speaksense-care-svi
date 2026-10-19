import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

LABELS = ["fear", "depression", "intimidation", "isolation", "suicidal"]

df = pd.read_csv("data/test2.csv", encoding="utf-8")
texts = df["text"].astype(str).tolist()
y = df[LABELS].values
print("Test sentences:", len(texts))


def prf(truth, pred):
    p, r, f, _ = precision_recall_fscore_support(
        truth, pred, average="binary", zero_division=0
    )
    return p, r, f


def show(title, preds):
    print("\n" + title)
    for i, name in enumerate(LABELS):
        p, r, f = prf(y[:, i], preds[:, i])
        print(
            f"  {name:13s} precision={p:.2f} recall={r:.2f} f1={f:.2f}"
            f"  (positives: {int(y[:, i].sum())})"
        )


# ---- trained model ----
from svi.text_analysis import analyse_text, CUTOFFS

res = [analyse_text(t) for t in texts]
scores = np.array([[r[l] for l in LABELS] for r in res])
cut = np.array(
    [max(CUTOFFS[l], 0.30) if l == "intimidation" else CUTOFFS[l] for l in LABELS]
)
show("TRAINED model, default cutoff 0.5", (scores > 0.5).astype(int))
show("TRAINED model, tuned cutoffs", (scores > cut).astype(int))

# ---- the actual safety flags the app uses ----
print("\nSYSTEM SAFETY FLAGS (model + keyword phrases)")
s_flag = np.array([int(r["suicide_flag"]) for r in res])
t_flag = np.array([int(r["threat_flag"]) for r in res])
p, r_, f = prf(y[:, 4], s_flag)
print(f"  suicide_flag vs suicidal label:     precision={p:.2f} recall={r_:.2f} f1={f:.2f}")
p, r_, f = prf(y[:, 2], t_flag)
print(f"  threat_flag vs intimidation label:  precision={p:.2f} recall={r_:.2f} f1={f:.2f}")

missed = [texts[i] for i in range(len(texts)) if y[i, 4] == 1 and not s_flag[i]]
print("\nSuicidal cases the system did NOT flag:", len(missed))
for m in missed:
    print("  -", m)


# ---- zero-shot baseline ----
try:
    from svi.text_analysis_zeroshot import analyse_text as zs_analyse

    zs = np.array([[zs_analyse(t)[l] for l in LABELS] for t in texts])
    show("ZERO-SHOT baseline, cutoff 0.5", (zs > 0.5).astype(int))
except Exception as error:
    print("\nZero-shot comparison skipped:", error)

# ---- save per-sentence scores for the report ----
out = df[["text"]].copy()
for i, l in enumerate(LABELS):
    out["score_" + l] = scores[:, i].round(3)
out["suicide_flag"] = s_flag
out["threat_flag"] = t_flag
out.to_csv("data/test2_results.csv", index=False, encoding="utf-8")
print("\nSaved data/test2_results.csv")
