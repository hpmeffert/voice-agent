import os
import subprocess
from pathlib import Path
from typing import Optional

# Piper wird NICHT mitgeliefert. Pfad kommt aus ENV oder ist im PATH.
PIPER_BIN = os.getenv("PIPER_BIN", "piper")
VOICES_DIR = Path(os.getenv("PIPER_VOICES_DIR", str(Path.home() / "models" / "piper-voices")))

VOICE_DE = os.getenv("PIPER_VOICE_DE", "de_DE-voice.onnx")
VOICE_EN = os.getenv("PIPER_VOICE_EN", "en_US-voice.onnx")

def speak(text: str, lang: Optional[str] = None, out_wav: Optional[Path] = None) -> None:
    if not text.strip():
        return

    if out_wav is None:
        out_wav = Path("/tmp/piper_last.wav")

    voice = VOICES_DIR / (VOICE_DE if (lang or "").startswith("de") else VOICE_EN)

    cmd = [PIPER_BIN, "-m", str(voice), "-f", str(out_wav)]
    subprocess.run(cmd, input=text.encode("utf-8"), check=True)
    subprocess.run(["afplay", str(out_wav)], check=False)