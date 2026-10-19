from svi.speech import transcribe
from svi.acoustic import acoustic_features, vocal_stress_score
from svi.text_analysis import analyse_text
from svi.scoring import compute_svi, categorize, recommend


def run(audio_path=None, text=None):
    lang = "text-input"
    feats = None
    if audio_path:
        text, lang = transcribe(audio_path)
        feats = acoustic_features(audio_path, text)
        vocal = vocal_stress_score(feats)
    else:
        vocal = 0.0  # no audio, so no vocal evidence

    t = analyse_text(text)
    svi = compute_svi(t, vocal)
    cat = categorize(svi, t)
    return {
        "language": lang,
        "transcript": text,
        "svi": svi,
        "category": cat,
        "text_scores": t,
        "vocal_score": vocal,
        "acoustic": feats,
        "recommendations": recommend(cat, t),
    }