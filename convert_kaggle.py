import pandas as pd

TEXT_COL = "statement"
STATUS_COL = "status"
LABELS = ["fear", "depression", "intimidation", "isolation", "suicidal"]

df = pd.read_csv("data/kaggle_mental_health.csv")
df = df[[TEXT_COL, STATUS_COL]].dropna()
df[STATUS_COL] = df[STATUS_COL].astype(str).str.strip().str.lower()

print(df[STATUS_COL].value_counts())

# status in the Kaggle file -> labels it switches on for your model
MAPPING = {
    "suicidal": {"suicidal": 1},
    "depression": {"depression": 1},
    "anxiety": {"fear": 1},   # rough stand-in for fear
    "normal": {},             # all zeros = negative examples
}

parts = []
for status, on in MAPPING.items():
    sub = df[df[STATUS_COL] == status]
    if sub.empty:
        print("WARNING: no rows for status", status)
        continue
    sub = sub.sample(n=min(500, len(sub)), random_state=1).copy()
    for col in LABELS:
        sub[col] = on.get(col, 0)
    parts.append(sub)

out = pd.concat(parts).rename(columns={TEXT_COL: "text"})
out = out[["text"] + LABELS].drop_duplicates(subset="text")
out.to_csv("data/kaggle_mapped.csv", index=False)
print("Saved", len(out), "rows to data/kaggle_mapped.csv")