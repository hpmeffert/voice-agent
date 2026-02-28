import sounddevice as sd
import numpy as np

fs = 16000
sec = 2
print("Recording 2 seconds...")
audio = sd.rec(int(sec*fs), samplerate=fs, channels=1, dtype="float32")
sd.wait()
rms = float(np.sqrt(np.mean(np.square(audio))))
print("RMS:", rms)