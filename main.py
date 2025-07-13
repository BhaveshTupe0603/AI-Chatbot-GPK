from voice_utils import speak, listen_voice_input
from chatbot import process_text_input  # your chatbot logic

# ----------------------------
# Main Chat Loop
# ----------------------------
if __name__ == "__main__":
    speak("🚖 Welcome to SmartBot! Your AI ride assistant is ready.")
    
    mode = input("Choose input mode (text/voice/exit): ").strip().lower()

    if mode == "exit":
        speak("Goodbye! Have a safe journey.")

    elif mode == "text":
        speak("How can I help you today? You can say things like 'Book a ride from Bagalur to Hosur', 'Show fare', or 'Track my driver'.")
        while True:
            user_input = input("You: ").strip()
            if user_input:
                response, should_exit = process_text_input(user_input)
                speak(response)
                if should_exit:
                    break

    elif mode == "voice":
        speak("How can I help you today? You can say things like 'Book a ride from Bagalur to Hosur', 'Show fare', or 'Track my driver'.")
        while True:
            user_input = listen_voice_input()  # ✅ fixed function name
            if user_input:
                response, should_exit = process_text_input(user_input)
                speak(response)
                if should_exit:
                    break

    else:
        speak("Invalid mode. Please restart and choose 'text' or 'voice'.")
