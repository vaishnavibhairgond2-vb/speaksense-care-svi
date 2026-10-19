import os
import tempfile
import streamlit as st
from svi.pipeline import run

st.set_page_config(page_title="Voice Distress Assessment", layout="centered")
st.title("Voice Distress Assessment - Prototype")

consent = st.checkbox("The speaker has given informed consent for this analysis")

st.write("Click the microphone, speak, click stop, then press **Analyse**.")
recording = st.audio_input("Record voice")
typed = st.text_area("Or type a narrative instead (optional)")

if st.button("Analyse", type="primary"):
    if not consent:
        st.warning("Consent is required before analysis.")
        st.stop()

    if recording is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(recording.getvalue())
            path = f.name
        try:
            with st.spinner("Transcribing and analysing... (first run is slow)"):
                res = run(audio_path=path)
        finally:
            os.remove(path)  # do not keep the caller's audio
    elif typed.strip():
        with st.spinner("Analysing..."):
            res = run(text=typed)
    else:
        st.warning("Record your voice or type a narrative first.")
        st.stop()

    cat = res["category"]
    st.metric("Stress Vulnerability Index (0-100)", res["svi"])
    if cat == "Critical":
        st.error("Risk category: Critical")
    elif cat == "High":
        st.error("Risk category: High")
    elif cat == "Moderate":
        st.warning("Risk category: Moderate")
    else:
        st.success("Risk category: Low")

    st.subheader("Transcript")
    st.write(res["transcript"])
    st.caption("Detected language: " + str(res["language"]))

    st.subheader("Recommended actions")
    for r in res["recommendations"]:
        st.write("-", r)

    st.subheader("Why this score (explainability)")
    t = res["text_scores"]
    for key in ["fear", "depression", "intimidation", "isolation", "suicidal"]:
        st.progress(min(max(float(t[key]), 0.0), 1.0), text=key.capitalize())
    st.write(
        "Suicide-risk flag:", t["suicide_flag"],
        "| Threat flag:", t["threat_flag"],
        "| Vocal stress:", round(res["vocal_score"], 2),
    )

    if res["acoustic"]:
        with st.expander("Voice measurements"):
            a = res["acoustic"]
            st.write("Pitch variation:", round(a["pitch_std"], 1))
            st.write("Pause ratio:", round(a["pause_ratio"], 2))
            st.write("Long pauses:", a["long_pauses"])
            st.write("Speech rate (words/sec):", round(a["speech_rate"], 2))
            st.write("Duration (sec):", round(a["duration"], 1))

    st.caption(
        "Decision support only. AI can miss distress or flag it wrongly. "
        "A trained human counsellor must make the final decision."
    )