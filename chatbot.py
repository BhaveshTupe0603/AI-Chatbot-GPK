import json
import pickle
import sqlite3 
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random
import re
from fare_utils import calculate_fare_by_address  # 🔁 Import fare logic
import uuid  # ✅ Add at the top of chatbot.py if not already
# ----------------------------
# Load model and files
# ----------------------------
model = load_model("chat_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

with open("intents_smartbot.json") as f:
    intents = json.load(f)

# ----------------------------
# Chat session memory
# ----------------------------
chat_state = {
    "pickup": None,
    "drop": None,
    "ride_type": None,
    "fare": None,                 # ✅ Add this line
    "fare_confirmed": False
}
# ----------------------------
# Chatbot response with state tracking
# ----------------------------
def process_text_input(text):
    global chat_state
    clean_text = text.lower().strip()

    # Manual exit
    if clean_text in ["exit", "quit", "bye"]:
        return "Goodbye! Have a safe journey.", True

    # If ride is in progress
    if "book" in clean_text and "ride" in clean_text:
        if not chat_state["pickup"] and not chat_state["drop"]:
            return "Sure! Please provide your pickup and drop locations.", False

    # From-to detection
    if "from" in clean_text and "to" in clean_text:
        pickup = extract_phrase_between(clean_text, "from", "to")
        drop = clean_text.split("to")[-1].strip()
        chat_state["pickup"] = pickup
        chat_state["drop"] = drop
        return "🚗 Got pickup and drop! Which ride would you like: Auto, Bike, Car, Cab, Taxi, Scooter, Sedan or SUV?", False

    # Only pickup
    if not chat_state["pickup"] and any(word in clean_text for word in ["pickup", "from"]):
        chat_state["pickup"] = extract_location(clean_text)
        return "✅ Got your pickup. What's your drop location?", False

    # Only drop
    if not chat_state["drop"] and any(word in clean_text for word in ["drop", "to", "destination"]):
        chat_state["drop"] = extract_location(clean_text)
        if not chat_state["pickup"]:
            return "📍 Got your drop. Now please tell me your pickup location.", False
        return "🚗 Great! What ride type do you prefer: Auto, Bike, Car, Cab, Taxi, Scooter, Sedan or SUV?", False

    # Ride type
    if any(ride in clean_text for ride in ["auto", "bike", "car", "cab", "taxi", "scooter", "sedan", "suv"]):
        chat_state["ride_type"] = extract_ride_type(clean_text)
        if chat_state["pickup"] and chat_state["drop"]:
            fare, msg = calculate_fare_by_address(
                chat_state["pickup"], chat_state["drop"], chat_state["ride_type"]
            )
            if fare is not None:
                chat_state["fare"] = fare 
                chat_state["fare_confirmed"] = True
                return f"{msg}\nShall I confirm your booking?", False
            else:
                return msg, False
        return "🚘 Please provide both pickup and drop before selecting ride type.", False

    # Confirm ride
    elif any(word in clean_text for word in ["yes", "confirm", "book now", "sure", "please book it"]):
        if not any([chat_state["pickup"], chat_state["drop"], chat_state["ride_type"]]):
            return "✅ Your ride is already confirmed. Anything else I can help with?", False

        if all([chat_state["pickup"], chat_state["drop"], chat_state["ride_type"]]):
            if chat_state["fare_confirmed"]:
                ride_id = str(uuid.uuid4())[:8]  # ✅ Generate short unique Ride ID

                summary = (
                    f"✅ Ride confirmed!\n📍 From: {chat_state['pickup']}\n"
                    f"📍 To: {chat_state['drop']}\n🚗 Ride: {chat_state['ride_type'].title()}\n"
                    f"🆔 Ride ID: {ride_id}\n"
                    f"🧑 Driver will arrive shortly. Thank you!"
                )
                ride_data = {
                    "pickup": chat_state["pickup"],
                    "drop": chat_state["drop"],
                    "ride_type": chat_state["ride_type"],
                    "fare": chat_state["fare"],
                    "ride_id": ride_id
                }
                reset_state()
                return summary, True, ride_data  # ✅ return ride info for DB
            else:
                return "📝 Please check fare before confirming the ride.", False

        return "❗ Please complete pickup, drop and ride type first.", False
    
    # ✅ Cancel ride by Ride ID
    cancel_match = re.search(r"(?:cancel.*ride.*|cancel ride)\s+(\w{8})", clean_text)
    if cancel_match:
        ride_id = cancel_match.group(1)
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()

        # Optional: check if ride exists before deleting
        cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
        ride = cursor.fetchone()

        if ride:
            cursor.execute("DELETE FROM rides WHERE ride_id = ?", (ride_id,))
            conn.commit()
            conn.close()
            return f"❌ Ride {ride_id} has been successfully cancelled.", False
        else:
            return f"⚠️ Ride ID {ride_id} not found.", False


    # Reset
    if any(word in clean_text for word in ["reset", "clear", "start over"]):
        reset_state()
        return "🔄 Ride info reset. Please start again.", False
    
    # ✅ Manual Complaint Trigger (before ML fallback)
    if "complaint" in clean_text or "issue" in clean_text or "problem" in clean_text or "report" in clean_text:
        return "🛑 Sorry to hear that. Please describe your issue below.", False, {"trigger": "open_complaint"}


        # ✅ Handle polite replies after reset like “thank you”
    if not any([chat_state["pickup"], chat_state["drop"], chat_state["ride_type"]]):
        polite_words = ["thank you", "thanks", "ok", "okay", "cool"]
        if clean_text in polite_words:
            return "You're welcome! 😊", False

    # ✅ Handle greetings early — let ML model respond
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    if clean_text in greetings:
        # Skip fallback — allow ML-based greeting response
        pass
    else:
        # ✅ Fallback slot-filling with input + keyword validation
        ride_related_keywords = ["book", "ride", "cab", "taxi", "driver", "fare", "find", "auto"]

        if not chat_state["pickup"] and is_valid_location_input(clean_text):
            if not any(word in clean_text for word in ride_related_keywords):
                chat_state["pickup"] = clean_text
                return "📍 Got your pickup location. Now tell me your drop location.", False

        if not chat_state["drop"] and is_valid_location_input(clean_text):
            if not any(word in clean_text for word in ride_related_keywords):
                chat_state["drop"] = clean_text
                return "📍 Got your drop location. What type of ride do you want: Auto, Bike, Car, Cab, Taxi, Scooter, Sedan or SUV?", False





    # ML-based fallback
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=20, truncating='post')
    prediction = model.predict(padded)
    print("🧠 Predicted tag:", prediction, "->", label_encoder.inverse_transform([np.argmax(prediction)])[0])
    tag = label_encoder.inverse_transform([np.argmax(prediction)])[0]
    

    # Intent-specific actions
    if tag == "cancel_ride":
        reset_state()
        return "❌ Your ride has been cancelled.", False

    elif tag == "change_ride":
        reset_state()
        return "🔁 Okay. Let's update your ride details. Start by saying: book a ride.", False

    elif tag == "schedule_ride":
        return "🕒 Ride scheduling is enabled. Please tell me pickup and drop.", False

    elif tag == "rebook_ride":
        return "🔁 Booking your last ride again. Please confirm to proceed.", False

    elif tag == "help":
        return "🧠 I can help you book a ride, check fare, cancel, or rebook. Just say 'Book a ride' to begin.", False

    elif tag == "complaint":
        return random.choice([
            "🛑 Sorry to hear that. Please describe your issue below.",
            "🛑 We'll take action. Kindly tell us what happened."
        ]), False, {"trigger": "open_complaint"}


    # Regular fallback response
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"]), False

    return "❓ Sorry, I didn't understand that.", False
# ----------------------------
# Helpers
# ----------------------------
def extract_location(text):
    match = re.search(r"(pickup|drop)?( location)?( is)?( at| to| from)? (.+)", text)
    if match:
        return match.group(5).strip()
    return text.strip()

def extract_phrase_between(text, start_word, end_word):
    try:
        return text.split(start_word)[1].split(end_word)[0].strip()
    except:
        return ""

def extract_ride_type(text):
    ride_types = {
        "auto": "auto",
        "bike": "bike",
        "scooter": "scooter",
        "car": "car",
        "cab": "cab",
        "taxi": "taxi",
        "sedan": "sedan",
        "suv": "suv"
    }
    for word in ride_types:
        if word in text.lower():
            return ride_types[word]
    return "car"  # Default fallback




def reset_state():
    global chat_state
    chat_state = {
        "pickup": None,
        "drop": None,
        "ride_type": None,
        "fare": None,   
        "fare_confirmed": False
    }

def is_valid_location_input(text):
    # Reject input that’s too long or has digits/specials
    return len(text.split()) <= 4 and text.replace(" ", "").isalpha()
