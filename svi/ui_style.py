import html

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

.stApp, .stApp p, .stApp label, .stApp li, .stApp textarea, .stApp button {
    font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif;
}
.stApp { background: #F4F8F7; }
.block-container { max-width: 880px; padding-top: 1.5rem; padding-bottom: 4rem; }
header[data-testid="stHeader"] { background: transparent; }

.stApp p, .stApp li, .stApp label { font-size: 1.3rem; line-height: 1.7; color: #10211F; }
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p { font-size: 1.4rem; }
textarea { font-size: 1.35rem !important; line-height: 1.6 !important; }

.stButton > button {
    background: #0F766E; color: white; border: none; border-radius: 14px;
    padding: 0.9rem 1rem; font-weight: 600;
}
.stButton > button:hover { background: #115E59; }
.stButton > button p { font-size: 1.6rem; color: white; font-weight: 600; }

.hero {
    background: linear-gradient(135deg, #0F766E, #14B8A6);
    border-radius: 24px; padding: 2rem 2rem 1.6rem; margin-bottom: 1.2rem;
}
.hero-title { font-size: 3.2rem; font-weight: 700; line-height: 1.2; color: white; }
.hero-sub { font-size: 1.4rem; margin-top: 0.7rem; color: #E6FFFA; line-height: 1.6; }

.notice {
    background: #E0F2FE; border-left: 6px solid #0284C7; color: #0C4A6E;
    padding: 1rem 1.2rem; border-radius: 12px; font-size: 1.15rem; line-height: 1.6;
}
.step {
    display: flex; align-items: center; gap: 0.8rem; font-size: 1.75rem;
    font-weight: 600; color: #134E4A; margin: 1.8rem 0 0.6rem;
}
.num {
    background: #0F766E; color: white; border-radius: 50%; width: 2.5rem; height: 2.5rem;
    display: inline-flex; align-items: center; justify-content: center; font-size: 1.3rem;
}
.title { font-size: 2.1rem; font-weight: 700; color: #134E4A; margin: 2rem 0 0.8rem; }

.risk { border: 3px solid; border-radius: 22px; padding: 1.6rem; text-align: center; margin: 1rem 0; }
.risk-label { font-size: 2.3rem; font-weight: 700; }
.risk-score { font-size: 4.6rem; font-weight: 700; line-height: 1.1; }
.risk-score span { font-size: 1.8rem; font-weight: 500; }
.risk-note { font-size: 1.05rem; opacity: 0.85; }

.alert {
    background: #FEE2E2; border-left: 8px solid #DC2626; color: #7F1D1D;
    padding: 1.1rem 1.3rem; border-radius: 14px; font-size: 1.3rem; font-weight: 600; margin: 0.8rem 0;
}
.crisis {
    background: #FFF7ED; border: 2px solid #FB923C; color: #7C2D12;
    padding: 1.2rem 1.4rem; border-radius: 16px; font-size: 1.3rem; line-height: 1.8; margin: 0.8rem 0;
}
.quote {
    background: white; border-radius: 16px; padding: 1.2rem 1.4rem; font-size: 1.45rem;
    line-height: 1.7; border: 1px solid #CBD5D1; color: #10211F;
}
.bar { margin: 0.9rem 0; }
.bar-top { display: flex; justify-content: space-between; font-size: 1.3rem; margin-bottom: 0.3rem; color: #10211F; }
.bar-bg { background: #E2E8F0; border-radius: 999px; height: 18px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; }
.rec {
    background: white; border-radius: 14px; border-left: 6px solid #0F766E;
    padding: 0.9rem 1.2rem; margin: 0.6rem 0; font-size: 1.3rem; color: #10211F;
}
.rec.urgent { border-left-color: #DC2626; background: #FEF2F2; font-weight: 600; }
.warn {
    background: #FEF9C3; border-left: 6px solid #CA8A04; color: #713F12;
    padding: 1rem 1.2rem; border-radius: 12px; font-size: 1.15rem; margin-top: 1.5rem;
}
.foot { text-align: center; color: #475569; font-size: 1.05rem; margin-top: 2.5rem; }
</style>
"""

HERO = """
<div class="hero">
  <div class="hero-title">💚 SpeakSense Care</div>
  <div class="hero-sub">Share your experience in your own words.<br>
  अपनी बात अपने शब्दों में बताइए · आपली गोष्ट आपल्या शब्दांत सांगा</div>
</div>
"""

NOTICE = """
<div class="notice">Experimental AI decision support only. The result is not a diagnosis
or a verified risk assessment. A trained human reviewer must make the final decision.</div>
"""

CATEGORY_STYLE = {
    "Low": ("#166534", "#DCFCE7", "Low risk"),
    "Moderate": ("#92400E", "#FEF3C7", "Moderate risk"),
    "High": ("#9A3412", "#FFEDD5", "High risk"),
    "Critical": ("#991B1B", "#FEE2E2", "Critical risk"),
}


def step(n, text):
    return f'<div class="step"><span class="num">{n}</span>{html.escape(text)}</div>'


def title(text):
    return f'<div class="title">{html.escape(text)}</div>'


def risk_card(svi, category):
    fg, bg, label = CATEGORY_STYLE.get(category, ("#334155", "#E2E8F0", str(category)))
    try:
        score = f"{float(svi):.0f}"
    except (TypeError, ValueError):
        score = "-"
    return (
        f'<div class="risk" style="background:{bg};border-color:{fg};color:{fg}">'
        f'<div class="risk-label">{label}</div>'
        f'<div class="risk-score">{score}<span>/100</span></div>'
        f'<div class="risk-note">Stress Vulnerability Index (experimental, not a probability)</div>'
        f'</div>'
    )


def alert(text):
    return f'<div class="alert">⚠️ {html.escape(text)}</div>'


def crisis_box():
    return (
        '<div class="crisis"><b>If someone is in immediate danger, call 112.</b><br>'
        'Tele-MANAS (mental health support): 14416<br>'
        'National Helpline Against Atrocities: 14566</div>'
    )


def quote(text):
    return f'<div class="quote">{html.escape(str(text))}</div>'


def bar(label, value):
    pct = int(max(0.0, min(1.0, float(value))) * 100)
    color = "#16A34A" if pct < 35 else ("#F59E0B" if pct < 65 else "#DC2626")
    return (
        f'<div class="bar"><div class="bar-top"><span>{html.escape(label)}</span><b>{pct}%</b></div>'
        f'<div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div></div>'
    )


def rec_card(text):
    css = "rec urgent" if str(text).startswith("URGENT") else "rec"
    return f'<div class="{css}">{html.escape(str(text))}</div>'