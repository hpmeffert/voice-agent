import os
import tempfile
import subprocess
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import FileResponse

app = FastAPI(title="Piper TTS Sidecar")

VOICE_DE = os.getenv("VOICE_DE", "/voices/de_DE-thorsten-medium.onnx")
VOICE_EN = os.getenv("VOICE_EN", "/voices/en_US-lessac-medium.onnx")
VOICE_SV = os.getenv("VOICE_SV", "/voices/sv_SE-nst-medium.onnx")
VOICE_NO = os.getenv("VOICE_NO", "/voices/no_NO-talesyntese-medium.onnx")
VOICE_FI = os.getenv("VOICE_FI", "/voices/fi_FI-harri-medium.onnx")

def pick_voice(lang: str | None) -> str:
    l = (lang or "").lower()
    if l.startswith("de"):
        return VOICE_DE
    if l.startswith("sv"):
        return VOICE_SV
    if l.startswith("no") or l.startswith("nb") or l.startswith("nn"):
        return VOICE_NO
    if l.startswith("fi"):
        return VOICE_FI
    if l.startswith("en"):
        return VOICE_EN
    return VOICE_EN

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tts")
def tts(text: str = Body(..., embed=True), lang: str | None = Body(None, embed=True)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty text")

    voice = pick_voice(lang)
    if not os.path.exists(voice):
        raise HTTPException(status_code=500, detail=f"Voice model not found: {voice}. Check voice mount and VOICE_* env vars.")

    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    # Piper CLI from piper-tts package provides `piper` executable
    cmd = ["piper", "-m", voice, "-f", out_path]
    try:
        subprocess.run(cmd, input=text.encode("utf-8"), check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Piper failed: {e}")

    return FileResponse(out_path, media_type="audio/wav", filename="speech.wav")