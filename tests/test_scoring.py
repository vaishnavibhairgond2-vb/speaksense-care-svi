from svi.scoring import compute_svi, categorize, recommend


def scores(**over):
    base = {
        "fear": 0.0, "depression": 0.0, "intimidation": 0.0,
        "isolation": 0.0, "suicidal": 0.0,
        "suicide_flag": False, "threat_flag": False,
        "suicide_strong": False, "threat_strong": False,
    }
    base.update(over)
    return base


def test_low_risk():
    t = scores()
    assert categorize(compute_svi(t, 0.0), t) == "Low"


def test_weak_suicide_flag_is_never_low():
    t = scores(suicide_flag=True)
    assert categorize(compute_svi(t, 0.0), t) in ("Moderate", "High", "Critical")


def test_strong_suicide_signal_is_critical():
    t = scores(suicide_flag=True, suicide_strong=True)
    assert categorize(compute_svi(t, 0.0), t) == "Critical"


def test_strong_threat_signal_is_critical():
    t = scores(threat_flag=True, threat_strong=True)
    assert categorize(compute_svi(t, 0.0), t) == "Critical"


def test_high_scores_give_critical():
    t = scores(fear=1, depression=1, intimidation=1, isolation=1, suicidal=1)
    assert categorize(compute_svi(t, 1.0), t) == "Critical"


def test_flag_adds_urgent_review_line():
    t = scores(suicide_flag=True)
    assert any("URGENT" in r for r in recommend("Moderate", t))
