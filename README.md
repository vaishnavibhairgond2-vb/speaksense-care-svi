# SpeakSense Care - SVI Prototype

AI decision-support prototype that analyses spoken or written narratives from victims
for possible distress indicators and produces a Stress Vulnerability Index (SVI,
0 to 100) with a risk category (Low, Moderate, High, Critical) and suggested next steps.

**This is a research prototype. It is not a diagnosis, not a validated clinical tool,
and must never make or act on decisions alone. A trained human reviewer decides.**

## How it works

1. Speech: Whisper transcribes audio (language auto-detected).
2. Voice features: pitch variation, pauses, speech rate, energy (librosa).
3. Text model: fine-tuned multilingual DistilBERT scores five indicators
   (fear, low mood, intimidation, social isolation, self-harm signal).
4. Safety layer: keyword phrases plus model cutoffs raise urgent flags.
5. Scoring: weighted SVI, category, recommendations, crisis numbers.

## Safety design

- A weak suicide or threat flag can never leave the case as Low (minimum Moderate).
- A strong signal (explicit phrase or very confident score) makes the case Critical.
- Every flag adds an "URGENT: human review" line.
- Flags favour recall over precision, so many flags are false alarms by design.
- Consent checkbox is required. Audio is deleted right after analysis.

## Setup (Windows, Python 3.12)

    python -m venv venv
    venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    winget install ffmpeg

Close and reopen the terminal after installing FFmpeg.

## Run

    streamlit run app.py          # web app with microphone
    python main.py --text "..."   # one text from the command line
    python main.py clip.wav       # one audio file
    python -m pytest              # tests for the scoring and safety rules

## Project layout

    app.py                  Streamlit interface
    main.py                 command-line entry point
    svi/                    speech, acoustic, text_analysis, scoring, pipeline, keywords, ui_style
    tests/                  scoring and safety tests
    train_text.py           fine-tunes the text model
    tune_thresholds.py      picks per-label cutoffs on the validation split
    evaluate_models.py      evaluation on a held-out set (use a copy for each new test set)
    merge_data.py           builds data/train.csv from the data sources
    data/                   datasets (not committed)
    models/                 trained model (not committed)

## Retraining

    python merge_data.py
    python train_text.py
    python tune_thresholds.py

## Data

- Kaggle "Sentiment Analysis for Mental Health" (English statements, labels mapped
  approximately: Suicidal to self-harm signal, Depression to low mood, Anxiety to
  fear, Normal to negatives). Research use only. Not redistributed here.
- Synthetic sentences in English, Hindi and Marathi written by the developers
  (threats, social boycott, indirect suicidal statements, negations, idioms).
- Check each source's licence and terms before reuse.

## Results (held-out set of 60 sentences, written by the developers)

| Label | Zero-shot F1 | Fine-tuned F1 |
|---|---|---|
| Fear | 0.60 | 0.67 |
| Low mood | 0.81 | 0.67 |
| Intimidation | 0.54 | 0.58 |
| Social isolation | 0.35 | 0.72 |
| Self-harm signal | 0.44 | 0.53 |
| Macro average | 0.55 | 0.63 |

Deployed safety flags (model plus keyword phrases): suicide flag caught 11 of 12
examples (precision 0.55); threat flag caught 14 of 15 (precision 0.45). The one
missed case was an explicit Hindi statement of intent; its phrase was added to the
keyword list afterwards, so these figures are from before that change.

## Limitations

- The 60 test sentences are three-language variants of only 20 situations, written by
  the same team as the training data. Real-world performance will be lower.
- Only 12 self-harm examples in the test set, so recall is statistically uncertain.
- Hindi and Marathi sentences were not reviewed by native-speaker clinicians.
- Cutoffs tuned on a small validation set did not transfer to new data.
- The model still raises false alarms on negated safety statements
  (for example "I am no longer afraid and I am safe").
- Keyword phrases are placeholders and need a clinician-approved list per language.
- Acoustic stress scoring is a heuristic and is not validated.
- Not validated on real helpline data, accents, code-mixed text or noisy audio.

## Before any real deployment

Counsellor-labelled data, native-speaker and clinical review, an independent
evaluation, privacy and consent review, and human-in-the-loop operating procedures.
