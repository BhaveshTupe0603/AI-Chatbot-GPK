import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

# Load Vosk model
model = Model("model")  # Make sure the 'model' folder exists

def test_vosk_voice():
    samplerate = 16000
    duration = 5  # seconds
    print("🎤 Listening... Speak something now")

    # Record audio
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    # Recognize
    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.AcceptWaveform(recording.tobytes())
    result = recognizer.Result()
    text = json.loads(result).get("text", "")

    print(f"🗣 You said: {text}")

if __name__ == "__main__":
    test_vosk_voice()
