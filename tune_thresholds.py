import json

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer

LABELS = ["fear", "depression", "intimidation", "isolation", "suicidal"]
MODEL_PATH = "models/svi_text"
TARGET_RECALL = 0.90

df = pd.read_csv("data/train.csv", encoding="utf-8")
df["text"] = df["text"].astype(str)
_, val_df = train_test_split(df, test_size=0.2, random_state=42)

tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

enc = tok(list(val_df["text"]), truncation=True, padding=True,
          max_length=64, return_tensors="pt")
with torch.no_grad():
    probs = torch.sigmoid(model(**enc).logits).numpy()
y = val_df[LABELS].values

thresholds = {}
print("Cutoffs chosen so recall is at least", TARGET_RECALL)
for i, name in enumerate(LABELS):
    best = 0.05
    for t in np.arange(0.95, 0.04, -0.05):
        pred = (probs[:, i] > t).astype(int)
        r = precision_recall_fscore_support(
            y[:, i], pred, average="binary", zero_division=0)[1]
        if r >= TARGET_RECALL:
            best = round(float(t), 2)
            break
    pred = (probs[:, i] > best).astype(int)
    p, r, f, _ = precision_recall_fscore_support(
        y[:, i], pred, average="binary", zero_division=0)
    thresholds[name] = best
    print(f"{name:13s} cutoff={best:.2f} precision={p:.2f} recall={r:.2f} "
          f"f1={f:.2f} (positives in validation: {int(y[:, i].sum())})")

with open(MODEL_PATH + "/thresholds.json", "w") as fh:
    json.dump(thresholds, fh)
print("Saved", MODEL_PATH + "/thresholds.json")
