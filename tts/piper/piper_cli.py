import os
import subprocess
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# lädt .env aus dem Projektroot (voice-agent/.env)
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=False)

from pathlib import Path
import os

def expand(p: str) -> str:
    # expands $HOME and ~
    return os.path.expandvars(os.path.expanduser(p))

PIPER_BIN = expand(os.getenv("PIPER_BIN", "piper"))
VOICES_DIR = Path(expand(os.getenv("PIPER_VOICES_DIR", str(Path.home() / "models" / "piper-voices"))))


VOICE_DE = os.getenv("PIPER_VOICE_DE", "de_DE-thorsten-medium.onnx")
VOICE_EN = os.getenv("PIPER_VOICE_EN", "en_US-lessac-medium.onnx")
VOICE_SV = os.getenv("PIPER_VOICE_SV", "sv_SE-nst-medium.onnx")
VOICE_FI = os.getenv("PIPER_VOICE_FI", "fi_FI-harri-medium.onnx")
VOICE_NO = os.getenv("PIPER_VOICE_NO", "no_NO-talesyntese-medium.onnx")

def speak(text: str, lang: Optional[str] = None, out_wav: Optional[Path] = None) -> None:
    if not text.strip():
        return
    if out_wav is None:
        out_wav = Path("/tmp/piper_last.wav")

    l = (lang or "").lower()

    if l.startswith("de"):
        voice_name = VOICE_DE
    elif l.startswith("sv"):
        voice_name = VOICE_SV
    elif l.startswith("no") or l.startswith("nb") or l.startswith("nn"):
    # no = generic Norwegian, nb = Bokmål, nn = Nynorsk
        voice_name = VOICE_NO
    elif l.startswith("fi"):
        voice_name = VOICE_FI
    elif l.startswith("en"):
        voice_name = VOICE_EN
    else:
        voice_name = VOICE_DE if any(ch in text for ch in "äöüÄÖÜß") else VOICE_EN

    voice_path = VOICES_DIR / voice_name
    
    # to print and see what language is used:
    PIPER_DEBUG = os.getenv("PIPER_DEBUG", "0") == "1"
    if PIPER_DEBUG:
        print(f"[PIPER] lang={lang} -> voice={voice_path}")
        
    subprocess.run([PIPER_BIN, "-m", str(voice_path), "-f", str(out_wav)],
                   input=text.encode("utf-8"),
                   check=True)
    subprocess.run(["afplay", str(out_wav)], check=False)