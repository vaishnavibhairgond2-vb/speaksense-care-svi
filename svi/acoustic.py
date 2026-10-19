import librosa
import numpy as np


def acoustic_features(audio_path, transcript=""):
    y, sr = librosa.load(audio_path, sr=16000)
    duration = len(y) / sr

    # Pitch variation
    f0, _, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sr,
    )
    f0 = f0[~np.isnan(f0)]
    pitch_std = float(np.std(f0)) if len(f0) else 0.0

    # Energy
    energy = float(np.mean(librosa.feature.rms(y=y)[0]))

    # Pauses
    intervals = librosa.effects.split(y, top_db=30)
    speech_time = sum(e - s for s, e in intervals) / sr
    pause_ratio = 1 - (speech_time / duration) if duration > 0 else 0
    gaps = [
        (intervals[i + 1][0] - intervals[i][1]) / sr
        for i in range(len(intervals) - 1)
    ]
    long_pauses = sum(1 for g in gaps if g > 0.7)

    # Speech rate (words per second)
    words = len(transcript.split())
    speech_rate = words / duration if duration > 0 else 0

    return {
        "pitch_std": pitch_std,
        "energy": energy,
        "pause_ratio": pause_ratio,
        "long_pauses": long_pauses,
        "speech_rate": speech_rate,
        "duration": duration,
    }


def vocal_stress_score(f):
    """Returns 0 to 1. Heuristic only. Calibrate with real labelled data."""
    pitch = min(f["pitch_std"] / 80, 1.0)
    pauses = min(f["pause_ratio"] / 0.5, 1.0)
    long_p = min(f["long_pauses"] / 10, 1.0)
    slow = 1.0 if f["speech_rate"] < 1.2 else 0.0
    return float(0.3 * pitch + 0.3 * pauses + 0.2 * long_p + 0.2 * slow)