import os
import time
import json
import queue
import numpy as np
import sounddevice as sd
import requests
from faster_whisper import WhisperModel
import subprocess
from tts.piper.piper_cli import speak

# ----------------------------
# Config
# ----------------------------
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_MAX_SECONDS = 12          # harte Obergrenze pro Aufnahme
SILENCE_TIMEOUT_SEC = 1.2        # wie lange Stille, bis Aufnahme stoppt
SILENCE_RMS_THRESHOLD = 0.012    # ggf. anpassen (Mikro/Umgebung)
WHISPER_MODEL = "small"          # "base", "small", "medium" ...
WHISPER_DEVICE = "cpu"           # "cpu" oder "cuda" (bei Nvidia)
WHISPER_COMPUTE = "int8"         # cpu: "int8" ist schnell

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

SYSTEM_PROMPT = (
    "Du bist ein hilfreicher, präziser Assistent. Antworte kurz, klar und korrekt. "
    "Wenn du unsicher bist, frage nach. Du kannst Deutsch und Englisch."
)

# ----------------------------
# Audio record (auto-stop on silence)
# ----------------------------
def record_until_silence():
    audio_q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        audio_q.put(indata.copy())

    print("\n🎙️ Sprich jetzt... (Stoppt automatisch bei Stille)")
    frames = []
    silence_start = None
    start = time.time()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32", callback=callback):
        while True:
            chunk = audio_q.get()
            frames.append(chunk)

            # RMS für Stille-Erkennung
            rms = float(np.sqrt(np.mean(np.square(chunk))))
            now = time.time()

            if rms < SILENCE_RMS_THRESHOLD:
                if silence_start is None:
                    silence_start = now
                elif (now - silence_start) >= SILENCE_TIMEOUT_SEC:
                    break
            else:
                silence_start = None

            if (now - start) >= RECORD_MAX_SECONDS:
                break

    audio = np.concatenate(frames, axis=0).reshape(-1)
    # normalize a bit (optional)
    peak = np.max(np.abs(audio)) if audio.size else 1.0
    if peak > 0:
        audio = audio / max(1.0, peak)
    print("⏹️ Aufnahme beendet.")
    return audio.astype(np.float32)

# ----------------------------
# STT: faster-whisper
# ----------------------------
#def transcribe(model, audio: np.ndarray):
#    # faster-whisper erwartet float32 array
#    segments, info = model.transcribe(audio, language=None, vad_filter=True)
#    text = "".join(seg.text for seg in segments).strip()
#    return text, info

def transcribe(model, audio):
    segments, info = model.transcribe(audio, language=None, vad_filter=True)
    text = "".join(seg.text for seg in segments).strip()
    lang = getattr(info, "language", None)  # "de", "en", "sv", ...
    return text, lang

# ----------------------------
# LLM: Ollama
# ----------------------------
def ask_ollama(user_text: str):
    prompt = f"{SYSTEM_PROMPT}\n\nUser:\n{user_text}\n\nAssistant:"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.4
        }
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data.get("response", "").strip()

# ----------------------------
# TTS: macOS "say" (DE/EN fallback)
# ----------------------------
#def speak(text: str):
#    if not text:
#       return
    # Stimme wählen: "Anna" (DE), "Samantha" (EN) sind oft vorhanden.
    # Wir wählen simpel: wenn viele ASCII? -> EN, sonst DE (grob).
    # Du kannst das später smarter machen.
#    voice = "Anna" if any(ch in text for ch in "äöüÄÖÜß") else "Samantha"
#    try:
#        subprocess.run(["say", "-v", voice, text], check=False)
#    except Exception as e:
#        print(f"(TTS Fehler: {e})")

def main():
    print("✅ Voice Agent (macOS) – STT (Whisper) → LLM (Ollama) → TTS (say)")
    print(f"🧠 Ollama Modell: {OLLAMA_MODEL}")
    print("Tipp: Setze OLLAMA_MODEL env var, z.B. OLLAMA_MODEL=llama3.1:8b")

    model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)

    while True:
        cmd = input("\n[Enter] zum Sprechen | 'q' zum Beenden: ").strip().lower()
        if cmd == "q":
            break

        audio = record_until_silence()
        #text, info = transcribe(model, audio)
        text, lang = transcribe(model, audio)

        if not text:
            print("🤷 Ich habe nichts verstanden. Versuch’s nochmal (Mikro/Threshold).")
            continue

        print(f"\n📝 Transkript: {text}")

        answer = ask_ollama(text)
        print(f"\n🤖 Antwort:\n{answer}")
        speak(answer, lang=lang)

if __name__ == "__main__":
    main()