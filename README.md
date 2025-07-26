# 🚖 AI-Chatbot-GPK – SmartBot for Ride Booking

SmartBot is an AI-powered chatbot designed to assist users with ride booking, fare estimation, support queries, and profile management. It supports both **text and voice input**, making ride services more accessible and efficient — just like Uber or Ola, but conversational!

---

## 📌 Features

### ✅ Welcome & Onboarding
- Greets users and introduces features
- Optionally supports language selection
- Explains how to interact with the chatbot

### 🚕 Ride Booking Flow
- Asks for pickup and drop-off locations
- Suggests ride options (Auto, Bike, Car)
- Confirms booking and shows driver details

### 💸 Fare Estimation
- Calculates estimated fare based on distance and ride type
- Real-time price updates using internal logic

### 📍 Ride Status
- Displays current and past ride details
- Shows driver's location (map integration placeholder)

### 👤 User Profile
- View last 5 rides
- Update personal info (name, contact, etc.)

### 🛠 Complaint & Support
- Report ride/payment issues
- Escalate to human support if needed
- Handles common FAQs (driver delay, payment failed, etc.)

### 🗣️ Voice & Text Support
- Voice input via OpenAI Whisper / Web Speech API
- NLP model trained on intent classification

---

## 🧠 Technologies Used

- **Python 3**
- **TensorFlow / Keras** – for training chatbot model
- **Scikit-learn** – label encoding
- **Flask** – for backend server/API
- **OpenAI Whisper / Web Speech API** – voice input
- **HTML/CSS/JS** – basic frontend templates
- **SQLite** – for user data and ride history
- **Git & GitHub** – version control and collaboration

---

## 📁 Project Structure

```
AI-Chatbot-GPK/
├── app.py                     # Flask app entry point
├── chatbot.py                # Chatbot logic and response handler
├── fare_utils.py             # Ride fare calculation
├── voice_utils.py            # Speech-to-text integration
├── chat_model.h5             # Trained ML model
├── tokenizer.pkl             # Tokenizer for intent processing
├── label_encoder.pkl         # Encodes intent labels
├── intents_smartbot.json     # Training data (intents/patterns/responses)
├── chat.db                   # SQLite database (users, rides, chats)
├── requirements.txt          # Python dependencies
├── Templates/
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   └── admin.html
├── static/                   # CSS, JS, images, etc.
├── test/                     # Unit test files
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone git@github.com:growwparktech/AI-Chatbot-GPK.git
cd AI-Chatbot-GPK
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Flask app
```bash
python app.py
```
Then visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🧪 Running Tests

```bash
pytest test/
```

---

## 🙋‍♂️ Contributors

- **Bhavesh Tupe & Harine K S** – Developer, AI Model Trainer, Backend Integration  
- **GrowwParkTech Team** – Management & Supervision

---

## 📄 License

This project is private and for internal use only under **GrowwParkTech**. Contact the admin for access or licensing details.

---

## 🔗 Contact

For queries or collaboration:  
📧 bhaveshtupe06@gmail.com  

