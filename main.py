import os
import time
import queue
import numpy as np
import sounddevice as sd
import requests
from faster_whisper import WhisperModel

from tts.piper.piper_cli import speak

# ----------------------------
# Config
# ----------------------------
SAMPLE_RATE = 16000
CHANNELS = 1

# Recording / VAD-ish
RECORD_MAX_SECONDS = int(os.getenv("RECORD_MAX_SECONDS", "20"))
SILENCE_TIMEOUT_SEC = float(os.getenv("SILENCE_TIMEOUT_SEC", "1.4"))
SILENCE_RMS_THRESHOLD = float(os.getenv("SILENCE_RMS_THRESHOLD", "0.010"))
START_GRACE_SEC = float(os.getenv("START_GRACE_SEC", "0.8"))   # give user time to start speaking
MIN_RECORD_SEC = float(os.getenv("MIN_RECORD_SEC", "1.5"))     # prevent too-early stop

# Whisper
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")  # base/small/medium
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "int8")

# Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.4"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "280"))  # limits response length (speed)

SYSTEM_PROMPT = (
    "Du bist ein hilfreicher, präziser Assistent. Antworte kurz, klar und korrekt. "
    "Wenn du unsicher bist, frage nach. "
    "Du kannst Deutsch, Englisch, Schwedisch, Norwegisch und Finnisch."
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
    grace_until = start + START_GRACE_SEC

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32", callback=callback):
        while True:
            chunk = audio_q.get()
            frames.append(chunk)

            rms = float(np.sqrt(np.mean(np.square(chunk))))
            now = time.time()

            # Allow a short grace period at the beginning
            if now < grace_until:
                if (now - start) >= RECORD_MAX_SECONDS:
                    break
                continue

            # Enforce minimum recording time before silence can stop it
            if (now - start) < MIN_RECORD_SEC:
                if (now - start) >= RECORD_MAX_SECONDS:
                    break
                continue

            if rms < SILENCE_RMS_THRESHOLD:
                if silence_start is None:
                    silence_start = now
                elif (now - silence_start) >= SILENCE_TIMEOUT_SEC:
                    break
            else:
                silence_start = None

            if (now - start) >= RECORD_MAX_SECONDS:
                break

    audio = np.concatenate(frames, axis=0).reshape(-1).astype(np.float32)
    print("⏹️ Aufnahme beendet.")
    return audio

# ----------------------------
# STT: faster-whisper
# ----------------------------
def transcribe(model, audio: np.ndarray):
    segments, info = model.transcribe(audio, language=None, vad_filter=True)
    text = "".join(seg.text for seg in segments).strip()
    lang = getattr(info, "language", None)  # e.g. "de", "en", "sv", "no"/"nb", "fi"
    return text, lang

# ----------------------------
# LLM: Ollama
# ----------------------------
def ask_ollama(user_text: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\n\nUser:\n{user_text}\n\nAssistant:"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": OLLAMA_NUM_PREDICT,
        },
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()
    return r.json().get("response", "").strip()

def main():
    print("✅ Voice Agent (macOS) – STT (Whisper) → LLM (Ollama) → TTS (Piper)")
    print(f"🧠 Ollama Modell: {OLLAMA_MODEL}")
    print(f"🎧 Whisper Modell: {WHISPER_MODEL}")

    model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)

    while True:
        cmd = input("\n[Enter] zum Sprechen | 'q' zum Beenden: ").strip().lower()
        if cmd == "q":
            break

        audio = record_until_silence()
        text, lang = transcribe(model, audio)

        if not text:
            print("🤷 Ich habe nichts verstanden. Versuch’s nochmal (Mikro/Threshold).")
            continue

        print(f"\n📝 Transkript ({lang}): {text}")

        answer = ask_ollama(text)
        print(f"\n🤖 Antwort:\n{answer}")

        # Piper TTS (uses your mapping de/en/sv/no/nb/nn/fi in piper_cli.py)
        speak(answer, lang=lang)

if __name__ == "__main__":
    main()
