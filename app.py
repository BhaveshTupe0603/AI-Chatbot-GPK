from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from chatbot import process_text_input
from fare_utils import geocode_address, ors_client
import sqlite3
import os
import uuid

app = Flask(__name__, static_url_path='/static')
app.secret_key = '123'  # ✅ Use a secure secret key in production




# ----------------------
# 🔌 SPLASH Functions
# ----------------------
@app.route('/splash')
def splash():
    return render_template('splash.html')


# ----------------------
# 🔌 Database Functions
# ----------------------
def get_db():
    conn = sqlite3.connect("chat.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_user(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return user

# ----------------------
# 🏠 Splash as Homepage
# ----------------------
@app.route('/')
def home():
    return redirect(url_for('splash'))

# ----------------------
# 💬 Main Chat UI
# ----------------------
@app.route('/chat')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    chats = db.execute(
        "SELECT message, sender FROM chats WHERE user_id = ? ORDER BY timestamp ASC",
        (session['user_id'],)
    ).fetchall()

    return render_template("index.html", username=session['username'], chats=chats)

# ----------------------
# 🛠️ Admin Dashboard
# ----------------------
@app.route('/admin')
def admin_dashboard():
    if session.get('username') != 'admin':
        return "Access denied", 403

    db = get_db()
    
    # ✅ Get all users
    users = db.execute("SELECT id, username, email, phone, updated_at FROM users").fetchall()

    # ✅ Get all rides (from `rides` table)
    rides = db.execute("""
        SELECT r.ride_id, u.username, r.pickup, r.drop_location, r.ride_type, r.fare, r.timestamp
        FROM rides r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.timestamp DESC
    """).fetchall()

    # ✅ Get all complaints (if complaint table exists)
    complaints = db.execute("SELECT * FROM complaints ORDER BY timestamp DESC").fetchall()

    return render_template("admin.html", users=users, rides=rides, complaints=complaints)


# ----------------------
# 🔐 Login
# ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pin = request.form['pin']

        user = get_user(username)
        if user and user['pin'] == pin:
            session['user_id'] = user['id']
            session['username'] = username
            if username == 'admin':
                return redirect(url_for('admin_dashboard'))  # ⬅️ Redirect admin to dashboard
            return redirect(url_for('index'))  # ⬅️ Regular users go to chatbot
        return "❌ Invalid login"

    return render_template("login.html")


# ----------------------
# 🆕 Register
# ----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pin = request.form['pin']

        if not pin.isdigit() or len(pin) != 4:
            return "❌ PIN must be exactly 4 digits."

        try:
            db = get_db()
            db.execute("INSERT INTO users (username, pin) VALUES (?, ?)", (username, pin))
            db.commit()
        except sqlite3.IntegrityError:
            return "❌ Username already exists"
        
        return redirect(url_for('login'))

    return render_template("login.html", register=True)

# ----------------------
# 🚪 Logout
# ----------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------------
# 💬 Chat Handling + Save History
# ----------------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get("message")

    user_id = session.get('user_id')
    response_data = process_text_input(message)

    response = None
    trigger = None

    # ✅ Support new return format: (response, _, ride_data/trigger dict)
    if isinstance(response_data, tuple) and len(response_data) == 3:
        response, _, ride_data = response_data

        if ride_data and user_id:
            # Save ride to DB if ride_id exists
            if "ride_id" in ride_data:
                db = get_db()
                db.execute("""
                    INSERT INTO rides (user_id, ride_id, pickup, drop_location, ride_type, fare)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    ride_data['ride_id'],
                    ride_data['pickup'],
                    ride_data['drop'],
                    ride_data['ride_type'],
                    ride_data['fare']
                ))
                db.commit()

            # ✅ If it's a special trigger like complaint
            if "trigger" in ride_data:
                trigger = ride_data["trigger"]

    else:
        response, _ = response_data  # Fallback to old format

    # ✅ Save chat history
    db = get_db()
    db.execute("INSERT INTO chats (user_id, message, sender) VALUES (?, ?, ?)", (user_id, message, 'user'))
    db.execute("INSERT INTO chats (user_id, message, sender) VALUES (?, ?, ?)", (user_id, response, 'bot'))
    db.commit()

    # ✅ Return response and optional trigger
    result = {"response": response}
    if trigger:
        result["trigger"] = trigger

    return jsonify(result)


# ----------------------
# 🗺️ Route API for Leaflet Map
# ----------------------
@app.route('/route')
def get_route():
    pickup = request.args.get("pickup")
    drop = request.args.get("drop")

    pickup_coords = geocode_address(pickup)
    drop_coords = geocode_address(drop)

    if not pickup_coords or not drop_coords:
        return jsonify({"error": "Invalid coordinates"}), 400

    try:
        route = ors_client.directions(
            [pickup_coords, drop_coords],
            profile='driving-car',
            format='geojson'
        )
        coordinates = route['features'][0]['geometry']['coordinates']  # [lon, lat]
        route_coords = [[lat, lon] for lon, lat in coordinates]

        return jsonify({
            "pickup_coords": [pickup_coords[1], pickup_coords[0]],
            "drop_coords": [drop_coords[1], drop_coords[0]],
            "route_coords": route_coords
        })
    except Exception as e:
        print("ORS routing error:", e)
        return jsonify({"error": "Route fetch failed"}), 500
    
@app.route('/complaint', methods=['POST'])
def complaint():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"status": "error", "message": "Empty complaint"}), 400

    db = get_db()
    db.execute("INSERT INTO complaints (user_id, username, message) VALUES (?, ?, ?)",(session['user_id'], session.get('username'), message))
    db.commit()

    return jsonify({"status": "success", "message": "Complaint submitted successfully."})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    db = get_db()
    db.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
    db.commit()
    return jsonify({"message": "✅ Chat history cleared!"})

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']

        db.execute("""
            UPDATE users 
            SET email = ?, phone = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (email, phone, session['user_id']))
        db.commit()

    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()

    # ✅ Fetch ride history for this user
    rides = db.execute("""
        SELECT ride_id, pickup, drop_location, ride_type, fare, timestamp
        FROM rides
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (session['user_id'],)).fetchall()

    return render_template('profile.html', user=user, rides=rides)



# ----------------------
# 🔄 Run the Flask app
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
