
WEIGHTS = {
    "fear": 0.20,
    "depression": 0.15,
    "intimidation": 0.15,
    "isolation": 0.10,
    "suicidal": 0.20,
    "vocal": 0.20,
}


def compute_svi(text_scores, vocal):
    total = (
        WEIGHTS["fear"] * text_scores["fear"]
        + WEIGHTS["depression"] * text_scores["depression"]
        + WEIGHTS["intimidation"] * text_scores["intimidation"]
        + WEIGHTS["isolation"] * text_scores["isolation"]
        + WEIGHTS["suicidal"] * text_scores["suicidal"]
        + WEIGHTS["vocal"] * vocal
    )
    return round(total * 100, 1)


def score_band(svi, text_scores):
    # The SVI category reflects the numeric score.
    # Safety flags are handled separately by the application.
    if svi <= 25:
        return "Low"
    if svi <= 50:
        return "Moderate"
    if svi <= 75:
        return "High"
    return "Critical"


def recommend(category, text_scores):
    recs = []

    # Safety signals are not discarded just because the SVI is low.
    if text_scores.get("suicide_flag", False):
        recs.append(
            "URGENT: Human review of possible suicidal ideation"
        )

    if text_scores.get("threat_flag", False):
        recs.append(
            "URGENT: Human review of possible threats or intimidation"
        )

    if category == "Low":
        recs += [
            "Standard grievance handling",
            "Share information on rights and schemes",
        ]
    elif category == "Moderate":
        recs += [
            "Counselling referral as appropriate",
            "Legal aid guidance",
        ]
    elif category == "High":
        recs += [
            "Priority human review",
            "Legal aid guidance",
            "Assess whether medical assistance is needed",
        ]
    else:
        recs += [
            "Prompt human assessment",
            "Assess immediate safety and support needs",
        ]

    if text_scores.get("isolation", 0) > 0.6:
        recs.append("Consider community or rehabilitation outreach")

    return recs



def categorize(svi, text_scores):
    """SVI band, raised by safety signals so a flag can never read as Low."""
    order = ["Low", "Moderate", "High", "Critical"]
    band = score_band(svi, text_scores)
    floor = "Low"
    if text_scores.get("suicide_flag") or text_scores.get("threat_flag"):
        floor = "Moderate"
    if text_scores.get("suicide_strong") or text_scores.get("threat_strong"):
        floor = "Critical"
    return max(band, floor, key=order.index)
