import tempfile
from pathlib import Path

import streamlit as st

from svi.pipeline import run
from svi.ui_style import (
    CSS, HERO, NOTICE, alert, bar, crisis_box, quote, rec_card, risk_card, step, title,
)

st.set_page_config(page_title="SpeakSense Care", page_icon="💚", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HERO, unsafe_allow_html=True)
st.markdown(NOTICE, unsafe_allow_html=True)

MIC = "🎙️ Speak / बोलिए"
TYPE = "⌨️ Type / लिखिए"

INDICATORS = [
    ("fear", "Fear / डर"),
    ("depression", "Low mood / उदासी"),
    ("intimidation", "Threat or intimidation / धमकी"),
    ("isolation", "Social isolation / अकेलापन"),
    ("suicidal", "Self-harm signal"),
]

st.markdown(step(1, "Consent / सहमति"), unsafe_allow_html=True)
consent = st.checkbox(
    "I confirm that informed consent and authorization have been obtained for this analysis."
)

st.markdown(step(2, "How would you like to share? / कैसे बताना चाहेंगे?"), unsafe_allow_html=True)
method = st.radio("Choose", [MIC, TYPE], horizontal=True, label_visibility="collapsed")

st.markdown(step(3, "Your message / आपका संदेश"), unsafe_allow_html=True)
recording = None
text = ""
if method == MIC:
    st.write("Click the microphone, speak naturally, then press stop.")
    recording = st.audio_input("Record your voice", sample_rate=16000)
    if recording is not None:
        st.audio(recording)
else:
    text = st.text_area(
        "Type here", placeholder="Write what happened, in any language...",
        height=170, label_visibility="collapsed",
    )

st.markdown(step(4, "Analyse / जाँचिए"), unsafe_allow_html=True)
go = st.button("🔍 Analyse my input", type="primary", use_container_width=True)

if go:
    if not consent:
        st.warning("Please confirm consent before analysis.")
        st.stop()
    if method == MIC and recording is None:
        st.warning("Please record your voice first.")
        st.stop()
    if method == TYPE and not text.strip():
        st.warning("Please type a message first.")
        st.stop()

    try:
        with st.spinner("Analysing your input... (the first run is slow)"):
            if method == MIC:
                temp_path = None
                try:
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        f.write(recording.getvalue())
                        temp_path = f.name
                    result = run(audio_path=temp_path)
                finally:
                    if temp_path and Path(temp_path).exists():
                        Path(temp_path).unlink()
            else:
                result = run(text=text.strip())
        st.session_state["analysis_result"] = result
    except Exception as error:
        st.error("Analysis failed.")
        st.code(str(error))
        st.stop()

result = st.session_state.get("analysis_result")

if result:
    scores = result.get("text_scores", {})
    category = result.get("category", "Unavailable")

    st.markdown(title("Result / नतीजा"), unsafe_allow_html=True)
    st.markdown(risk_card(result.get("svi", 0), category), unsafe_allow_html=True)

    if scores.get("suicide_flag"):
        st.markdown(alert("Possible suicidal thoughts detected. A counsellor must review this case now."),
                    unsafe_allow_html=True)
    if scores.get("threat_flag"):
        st.markdown(alert("Possible threat or intimidation detected. Please review urgently."),
                    unsafe_allow_html=True)
    if category == "Critical" or scores.get("suicide_flag"):
        st.markdown(crisis_box(), unsafe_allow_html=True)

    st.markdown(title("What was heard / जो सुना गया"), unsafe_allow_html=True)
    st.markdown(quote(result.get("transcript") or "No transcript was returned."), unsafe_allow_html=True)
    st.caption("Detected language: " + str(result.get("language", "unknown")))

    st.markdown(title("Indicators / संकेत"), unsafe_allow_html=True)
    for key, label in INDICATORS:
        if isinstance(scores.get(key), (int, float)):
            st.markdown(bar(label, scores[key]), unsafe_allow_html=True)
    st.caption("Model scores, not probabilities. The isolation score is the least reliable.")

    st.markdown(title("Recommended next steps / अगले कदम"), unsafe_allow_html=True)
    recs = result.get("recommendations", [])
    if recs:
        for item in recs:
            st.markdown(rec_card(item), unsafe_allow_html=True)
    else:
        st.markdown(rec_card("No recommendations returned. Arrange independent human review."),
                    unsafe_allow_html=True)

    acoustic = result.get("acoustic")
    if acoustic:
        with st.expander("Voice measurements"):
            st.write("Pitch variation:", round(acoustic["pitch_std"], 1))
            st.write("Pause ratio:", round(acoustic["pause_ratio"], 2))
            st.write("Long pauses:", acoustic["long_pauses"])
            st.write("Speech rate (words/sec):", round(acoustic["speech_rate"], 2))
            st.write("Duration (sec):", round(acoustic["duration"], 1))

    st.markdown(
        '<div class="warn">AI can miss distress or flag it wrongly. '
        'A trained human reviewer must make the final assessment.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="foot">SpeakSense Care · Prototype · Human review required</div>',
            unsafe_allow_html=True)