import sounddevice as sd #sound device of PC
import soundfile as sf #sound file
import io #input/output
import speech_recognition as sr #speech 
import pyttsx3 
import re 

# Initialize TTS engine
def initialize_tts():
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # male voice
    engine.setProperty('rate', 150) 
    return engine 

engine = initialize_tts()

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002500-\U00002BEF"  # Chinese/Japanese characters
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def speak(text):
    print(f"SmartBot: {text}")           # Show full emoji-rich message to user
    clean_text = remove_emojis(text)     # Strip emojis only for TTS
    engine.say(clean_text)
    engine.runAndWait()



# Voice input using sounddevice and soundfile
def listen_voice_input():
    try:
        duration = 5  # seconds
        samplerate = 16000  # Hz
        speak("🎤 Listening... Please speak now.")
        print("Recording...")
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        # Save to buffer
        buf = io.BytesIO()
        sf.write(buf, recording, samplerate, format='WAV')
        buf.seek(0)

        # Use recognizer to transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(buf) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language='en-in')
            print(f"You (voice): {text}")
            return text

    except sr.UnknownValueError:
        speak("❌ Sorry, I couldn't understand your voice.")
    except sr.RequestError:
        speak("⚠️ Network error.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")
    
    return None
