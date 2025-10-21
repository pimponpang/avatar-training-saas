
from faster_whisper import WhisperModel
import tempfile

_model = WhisperModel("small", device="cpu", compute_type="int8")

def wav_bytes_to_text(wav_bytes: bytes, language: str = "ja") -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(wav_bytes); f.flush()
        segments, info = _model.transcribe(f.name, language=language, vad_filter=True, beam_size=1)
        return "".join([seg.text for seg in segments]).strip()
