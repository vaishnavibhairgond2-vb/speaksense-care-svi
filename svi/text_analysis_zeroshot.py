
import re
from transformers import pipeline


# Load the zero-shot classification model
_clf = pipeline(
    "zero-shot-classification",
    model="joeddav/xlm-roberta-large-xnli",
)


# Positive hypotheses for each indicator
HYPOTHESES = {
    "fear": (
        "The person's current emotional state is {}.",
        "experiencing fear or feeling unsafe",
    ),
    "depression": (
        "The person's current emotional state is {}.",
        "feeling hopeless, deeply sad, or helpless",
    ),
    "intimidation": (
        "The person's current situation involves {}.",
        "being threatened, coerced, or intimidated by another person",
    ),
    "isolation": (
        "The person's current social situation is {}.",
        "being excluded, isolated, or rejected by their community",
    ),
    "suicidal": (
        "The person's statement indicates {}.",
        "thoughts of suicide or wanting to end their own life",
    ),
}


# Contrast labels used to compare positive and negative evidence
CONTRAST_LABELS = {
    "fear": "not expressing fear or feeling unsafe",
    "depression": "not expressing hopelessness or deep sadness",
    "intimidation": "not describing threats, coercion, or intimidation",
    "isolation": "feeling socially connected and supported",
    "suicidal": (
        "not expressing thoughts of suicide or wanting to die"
    ),
}


# Direct expressions related to suicidal ideation.
# These are screening patterns, not a complete language detector.
SUICIDE_PATTERNS = [
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bwant to die\b",
    r"\bi want to end it all\b",
    r"\bthinking about suicide\b",
    r"\bthink(?:ing)? of suicide\b",
    r"\bsuicidal thoughts?\b",
    r"\bno reason to live\b",
    r"\bi don't want to live\b",
    r"\bi do not want to live\b",
    r"\bi wish i were dead\b",
    r"जीना नहीं चाहता",
    r"जीना नहीं चाहती",
    r"मरना चाहता",
    r"मरना चाहती",
    r"आत्महत्या",
    r"जगायचं नाही",
    r"मरावंसं वाटतं",
]


# Common explicit negations of suicidal thoughts
NEGATION_PATTERNS = [
    r"\bi do not want to (?:die|kill myself|end my life)\b",
    r"\bi don't want to (?:die|kill myself|end my life)\b",
    r"\bi am not thinking about suicide\b",
    r"\bi'm not thinking about suicide\b",
    r"\bi am not suicidal\b",
    r"\bi'm not suicidal\b",
    r"\bi do not want to hurt myself\b",
    r"\bi don't want to hurt myself\b",
    r"मुझे आत्महत्या नहीं करनी",
    r"मैं आत्महत्या नहीं करना चाहता",
    r"मैं आत्महत्या नहीं करना चाहती",
]


# Common expressions indicating threats or intimidation
THREAT_PATTERNS = [
    r"\bthey will kill me\b",
    r"\bthey threatened to kill me\b",
    r"\bthreatened to kill me\b",
    r"\bthreatening to kill me\b",
    r"\bwill burn me\b",
    r"\bwill beat me\b",
    r"\bthreatened me\b",
    r"\bthreatening me\b",
    r"\bthey threatened\b",
    r"\bhe threatened\b",
    r"\bshe threatened\b",
    r"जान से मार",
    r"धमकी",
    r"मारून टाकू",
    r"धमकावलं",
]


def _score(text, template, label, contrast_label):
    """
    Compare a positive indicator with its contrast label.

    The returned value is a model score, not a calibrated
    probability or a clinical risk estimate.
    """
    result = _clf(
        text,
        candidate_labels=[label, contrast_label],
        hypothesis_template=template,
        multi_label=False,
    )

    # Locate the positive label in the returned results
    positive_index = result["labels"].index(label)

    return float(result["scores"][positive_index])


def _matches(text, patterns):
    """Return True if any supplied pattern matches the text."""
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in patterns
    )


def analyse_text(text):
    """
    Analyse text for experimental distress indicators.

    Returns:
        fear, depression, intimidation, isolation, suicidal:
            Relative model scores.
        suicide_flag, threat_flag:
            Keyword-based screening flags.
        suicide_review, threat_review:
            Flags indicating that a human should review the text.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please provide some text to analyse.")

    text = text.strip()
    low = text.casefold()

    # Calculate scores for each indicator
    scores = {
        key: _score(
            text,
            template,
            label,
            CONTRAST_LABELS[key],
        )
        for key, (template, label) in HYPOTHESES.items()
    }

    # Check for explicit threat expressions
    threat_flag = _matches(low, THREAT_PATTERNS)

    # Check for explicit suicidal expressions and common negations
    negated_suicide_phrase = _matches(
        low,
        NEGATION_PATTERNS,
    )

    suicide_phrase = _matches(
        low,
        SUICIDE_PATTERNS,
    )

    # A simple screening rule; mixed statements and complex
    # negation still require human review.
    suicide_flag = bool(
        suicide_phrase and not negated_suicide_phrase
    )

    return {
        "fear": scores["fear"],
        "depression": scores["depression"],
        "intimidation": scores["intimidation"],
        "isolation": scores["isolation"],
        "suicidal": scores["suicidal"],
        "suicide_flag": suicide_flag,
        "threat_flag": bool(threat_flag),
        "suicide_review": suicide_flag,
        "threat_review": bool(threat_flag),
    }
