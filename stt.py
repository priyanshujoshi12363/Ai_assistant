from faster_whisper import WhisperModel

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)


def speech_to_text(audio_path):

    segments, info = model.transcribe(
        audio_path,
        beam_size=1,
        vad_filter=True
    )

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()