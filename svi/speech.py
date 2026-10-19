import whisper

_model = whisper.load_model("small")  # use "medium" for better Hindi/Marathi accuracy


def transcribe(audio_path):
    result = _model.transcribe(audio_path, task="transcribe")  # language auto-detected
    return result["text"].strip(), result["language"]