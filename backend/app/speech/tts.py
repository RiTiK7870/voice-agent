import pyttsx3

from app.config import SPEECH_PROVIDER


_engine = None


def _get_engine():
    global _engine

    if _engine is None:
        _engine = pyttsx3.init()

        # Slightly slower and clearer for a voice-agent demo
        _engine.setProperty("rate", 165)

    return _engine


def synthesize_speech(text: str) -> bytes:
    """
    Convert text to WAV audio bytes.

    Local POC:
        text -> pyttsx3 -> WAV file -> bytes

    Later:
        Replace this with the TCS-approved TTS service.
    """

    if not text.strip():
        return b""

    if SPEECH_PROVIDER == "mock":
        import tempfile
        from pathlib import Path

        engine = _get_engine()

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:
            output_path = temp_file.name

        try:
            engine.save_to_file(text, output_path)
            engine.runAndWait()

            audio_bytes = Path(output_path).read_bytes()

            return audio_bytes

        finally:
            Path(output_path).unlink(missing_ok=True)

    if SPEECH_PROVIDER == "azure":
        raise NotImplementedError(
            "Azure/TCS TTS integration will be added "
            "when approved credentials/configuration are provided."
        )

    raise RuntimeError(
        f"Unsupported SPEECH_PROVIDER: {SPEECH_PROVIDER}"
    )