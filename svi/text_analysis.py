import json
import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from svi.keywords import SUICIDE_KEYWORDS, THREAT_KEYWORDS

MODEL_PATH = "models/svi_text"
LABELS = ["fear", "depression", "intimidation", "isolation", "suicidal"]

_tok = AutoTokenizer.from_pretrained(MODEL_PATH)
_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
_model.eval()

# Per-label cutoffs tuned on the validation set (see tune_thresholds.py)
with open(os.path.join(MODEL_PATH, "thresholds.json")) as fh:
    CUTOFFS = json.load(fh)


STRONG_SUICIDE = 0.85   # model-only score treated as an urgent signal


def analyse_text(text):
    enc = _tok(text, return_tensors="pt", truncation=True, max_length=64)
    with torch.no_grad():
        probs = torch.sigmoid(_model(**enc).logits)[0].tolist()
    s = dict(zip(LABELS, probs))

    low = text.lower()
    suicide_kw = any(k in low for k in SUICIDE_KEYWORDS)
    threat_kw = any(k in low for k in THREAT_KEYWORDS)

    # weak signal: model score above its tuned cutoff, or a keyword
    suicide_flag = suicide_kw or s["suicidal"] > min(max(CUTOFFS["suicidal"], 0.15), 0.50)
    threat_flag = threat_kw or s["intimidation"] > max(CUTOFFS["intimidation"], 0.10)
    # strong signal: explicit phrase, or a very confident model score
    suicide_strong = suicide_kw or s["suicidal"] >= STRONG_SUICIDE
    threat_strong = threat_kw

    return {
        "fear": s["fear"],
        "depression": s["depression"],
        "intimidation": s["intimidation"],
        "isolation": s["isolation"],
        "suicidal": s["suicidal"],
        "suicide_flag": suicide_flag,
        "threat_flag": threat_flag,
        "suicide_strong": suicide_strong,
        "threat_strong": threat_strong,
    }




