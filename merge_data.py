import os
import pandas as pd

LABELS = ["fear", "depression", "intimidation", "isolation", "suicidal"]
FILES = [
    "data/kaggle_mapped.csv",
    "data/goemotions_mapped.csv",
    "data/synthetic.csv", "data/synthetic2.csv", "data/synthetic3.csv",
]

parts = []
for f in FILES:
    if not os.path.exists(f):
        print("skipping (not found):", f)
        continue
    d = pd.read_csv(f, encoding="utf-8")
    if "kaggle" in f or "goemotions" in f:
        # Public data is long and English-only. Keep short texts only and cap
        # the amount, so it doesn't swamp the small domain dataset.
        d = d[d["text"].astype(str).str.len() <= 300]
        d = d.sample(n=min(500, len(d)), random_state=1)
    print(f, len(d), "rows")
    parts.append(d)

df = pd.concat(parts).drop_duplicates(subset="text")
df = df.sample(frac=1, random_state=1)
df.to_csv("data/train.csv", index=False, encoding="utf-8")

print("Total rows:", len(df))
print(df[LABELS].sum())
