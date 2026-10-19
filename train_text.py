import json

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

LABELS = ["fear", "depression", "intimidation", "isolation", "suicidal"]
BASE_MODEL = "distilbert-base-multilingual-cased"
OUT_DIR = "models/svi_text"

df = pd.read_csv("data/train.csv", encoding="utf-8")
df["text"] = df["text"].astype(str)
train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
print("train rows:", len(train_df), "| validation rows:", len(val_df))

# Extra weight for rare labels (negatives / positives, capped)
pos = train_df[LABELS].sum().values.astype("float32")
neg = len(train_df) - pos
POS_WEIGHT = torch.tensor(np.clip(neg / np.maximum(pos, 1), 1, 15), dtype=torch.float32)
print("pos_weight:", dict(zip(LABELS, POS_WEIGHT.tolist())))

tok = AutoTokenizer.from_pretrained(BASE_MODEL)


class TextDS(Dataset):
    def __init__(self, d):
        self.enc = tok(list(d["text"]), truncation=True, padding=True, max_length=64)
        self.y = d[LABELS].values.astype("float32")

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        item = {k: torch.tensor(v[i]) for k, v in self.enc.items()}
        item["labels"] = torch.tensor(self.y[i])
        return item


class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=POS_WEIGHT.to(outputs.logits.device))
        loss = loss_fn(outputs.logits, labels)
        return (loss, outputs) if return_outputs else loss


def metrics(eval_pred):
    logits, y = eval_pred
    probs = 1 / (1 + np.exp(-logits))
    pred = (probs > 0.5).astype(int)
    out = {}
    _, per_r, per_f, _ = precision_recall_fscore_support(
        y, pred, average=None, zero_division=0
    )
    for name, r, f in zip(LABELS, per_r, per_f):
        out["recall_" + name] = float(r)
        out["f1_" + name] = float(f)
    return out


model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    num_labels=len(LABELS),
    problem_type="multi_label_classification",
)

args = TrainingArguments(
    output_dir="models/checkpoints",
    num_train_epochs=8,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=4e-5,
    eval_strategy="epoch",
    save_strategy="no",
    logging_steps=20,
    report_to="none",
    dataloader_pin_memory=False,
)

val_ds = TextDS(val_df)
trainer = WeightedTrainer(
    model=model,
    args=args,
    train_dataset=TextDS(train_df),
    eval_dataset=val_ds,
    compute_metrics=metrics,
)
trainer.train()
print(trainer.evaluate())
trainer.save_model(OUT_DIR)
tok.save_pretrained(OUT_DIR)
print("Saved to", OUT_DIR)
