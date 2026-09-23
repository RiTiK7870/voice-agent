from pathlib import Path
from tempfile import NamedTemporaryFile

from faster_whisper import WhisperModel

from app.config import SPEECH_PROVIDER


# Small local model for the POC.
# It downloads once and then runs locally.
_MODEL_SIZE = "base"

_model = WhisperModel(
    _MODEL_SIZE,
    device="cpu",
    compute_type="int8",
)


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Convert audio bytes into text.

    For the local POC:
        audio bytes -> temporary audio file -> Whisper -> text

    Later:
        Replace this with the TCS-approved STT service.
    """

    if not audio_bytes:
        return ""

    if SPEECH_PROVIDER == "mock":
        with NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:

            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        try:
            segments, info = _model.transcribe(
                temp_path,
                beam_size=5,
            )

            transcript = " ".join(
                segment.text.strip()
                for segment in segments
                if segment.text.strip()
            )

            return transcript.strip()

        finally:
            Path(temp_path).unlink(
                missing_ok=True
            )

    if SPEECH_PROVIDER == "azure":
        raise NotImplementedError(
            "Azure/TCS STT integration will be added "
            "when approved credentials/configuration are provided."
        )

    raise RuntimeError(
        f"Unsupported SPEECH_PROVIDER: {SPEECH_PROVIDER}"
    )