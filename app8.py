# app7.py — Final Clean Production Version
import os
from flask import Flask, request, render_template, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client
import math

import json
import random





# Twilio import (optional, will be None if not configured)
try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None


# ---------------------------------------------------------
# CONFIG — Supabase Credentials
# ---------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "change_me")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Supabase keys missing! Set in Render environment settings.")




supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# Twilio Config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")


# Initialize Twilio client
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TwilioClient:
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        print("Twilio init failed:", e)
        twilio_client = None

# ---------------------------------------------------------
# AI ADVICE — Load intents.json
# ---------------------------------------------------------
# ---------------------------------------------------------
# AI ADVICE — Load intents.json + helper
# ---------------------------------------------------------
try:
    with open("intents.json", "r", encoding="utf-8") as f:
        INTENTS = json.load(f)["intents"]
        print("💡 Loaded AI intents:", len(INTENTS))

    # Helper — split bilingual replies (English / Hindi)
    def parse_bilingual_text(text, lang):
        parts = text.split(" / ")
        if lang == "hi" and len(parts) > 1:
            return parts[1].strip()
        return parts[0].strip()

except Exception as e:
    print("❌ Error loading intents.json:", e)
    INTENTS = []



# Flask setup
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = SECRET_KEY


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def is_logged_in():
    return "user_id" in session

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# -------------------------
# Mock places (DEV MODE)
# -------------------------
MOCK_PLACES = [

    
    {"place_id":"dev_1","name":"Village Health Centre","address":"Village A","phone":"+919877751199","lat":18.5304,"lng":73.8567},
    {"place_id":"dev_2","name":"Swasthya Clinic","address":"Town B","phone":"+919351193352","lat":18.5384,"lng":73.8742},
    {"place_id":"dev_3","name":"Govt. Hospital","address":"Taluka C","phone":"+919766103689","lat":18.5404,"lng":73.8801}


    
]


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

# ---------- HOME (Protected Dashboard) ----------
@app.route("/")
def home():
    if not is_logged_in():
        return redirect("/login")
    return render_template("index.html")   # YOUR REAL UI IS USED HERE


# Notify doctor via SMS (Twilio)
@app.route("/notify-doctor-sms", methods=["POST"])
def notify_doctor_sms():
    data = request.get_json(silent=True) or {}

    doctor_phone = data.get("doctor_phone")
    patient_name = data.get("patient_name", "")
    date = data.get("date", "")
    time = data.get("time", "")
    notes = data.get("notes", "")

    if not doctor_phone:
        return jsonify({"success": False, "error": "no doctor phone"}), 400

    if not twilio_client:
        return jsonify({"success": False, "error": "Twilio not configured"}), 501

    message_body = (
        f"New appointment booked:\n"
        f"Patient: {patient_name}\n"
        f"Date: {date}\n"
        f"Time: {time}\n"
        f"Notes: {notes}"
    )

    try:
        msg = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_FROM_NUMBER,
            to=doctor_phone
        )
        return jsonify({"success": True, "sid": msg.sid})
    except Exception as e:
        print("Twilio send error:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    

    # ---------------------------------------------------------
# AI ADVICE BOT — handle symptom messages
# ---------------------------------------------------------
# ---------------------------------------------------------
# AI ADVICE BOT — handle symptom messages
# ---------------------------------------------------------
@app.route("/get", methods=["POST"])
def get_bot_response():
    data = request.get_json() or {}
    user_msg = (data.get("msg") or "").lower().strip()
    lang = data.get("lang", "en")

    # Match patterns
    for intent in INTENTS:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_msg:
                raw_reply = random.choice(intent["responses"])
                reply = parse_bilingual_text(raw_reply, lang)
                suggestions = intent.get("suggestions", [])
                return jsonify({"reply": reply, "suggestions": suggestions})

    # Fallback if no pattern matched
    fallback_responses = [
        "🤔 I'm not quite sure I understand. Could you describe your symptoms in more detail? / मुझे ठीक से समझ नहीं आया। क्या आप अपने लक्षण विस्तार से बता सकते हैं?",
        "🩺 I want to help you! Can you tell me what's bothering you? / मैं आपकी मदद करना चाहता हूँ! कृपया बताएं क्या परेशानी है?",
        "💙 I'm here for you! Please describe your symptoms so I can guide you better. / मैं आपके लिए यहाँ हूँ! अपने लक्षण बताएं ताकि मैं बेहतर मदद कर सकूं।"
    ]

    raw_fallback = random.choice(fallback_responses)
    fallback_reply = parse_bilingual_text(raw_fallback, lang)

    suggestions = [
        "🌡️ Fever / बुखार",
        "🤕 Headache / सिरदर्द",
        "🤧 Cough / खांसी",
        "😷 Sore throat / गला"
    ]

    return jsonify({"reply": fallback_reply, "suggestions": suggestions})





# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if is_logged_in():
            return redirect("/")
        return render_template("login.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if not username or not password:
        return render_template("login.html", error="Please enter username + password")

    # Fetch user from Supabase
    try:
        res = supabase.table("users").select("*").eq("username", username).execute()
    except Exception as e:
        return render_template("login.html", error="Server error: " + str(e))

    if not res.data:
        return render_template("login.html", error="Invalid username or password")

    user = res.data[0]

    stored_pw = user.get("password_hash") or user.get("password")

    if not stored_pw or not check_password_hash(stored_pw, password):
        return render_template("login.html", error="Invalid username or password")

    # SUCCESS → create session
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["full_name"] = user.get("full_name")

    return redirect("/")

@app.route("/nearby-doctors", methods=["GET"])
def nearby_doctors():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "missing coords"}), 400

    try:
        latf = float(lat)
        lonf = float(lon)
    except ValueError:
        return jsonify({"error": "invalid coords"}), 400

    # DEV MODE — return mock places with correct distance
    results = []
    for place in MOCK_PLACES:
        p = place.copy()
        distance = haversine(latf, lonf, p["lat"], p["lng"])
        p["distance_km"] = round(distance, 2)
        results.append(p)

    # Sort by distance
    results.sort(key=lambda x: x["distance_km"])

    return jsonify({"places": results})




# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if is_logged_in():
            return redirect("/")
        return render_template("signup.html")

    form = request.form
    username = (form.get("username") or "").strip()
    password = form.get("password") or ""
    full_name = (form.get("full_name") or "").strip()
    dob = form.get("dob") or None
    age = form.get("age") or None
    phone = (form.get("phone") or "").strip()
    email = (form.get("email") or "").strip()

    if not username or not password or not email:
        return render_template("signup.html", error="Username, password, email required")

    # Check for existing user
    try:
        exists = supabase.table("users").select("id").or_(
            f"username.eq.{username},email.eq.{email}"
        ).execute()
    except Exception as e:
        return render_template("signup.html", error="Server error: " + str(e))

    if exists.data:
        return render_template("signup.html", error="Username or email already exists")

    # Hash password
    pw_hash = generate_password_hash(password)

    payload = {
        "username": username,
        "password_hash": pw_hash,
        "full_name": full_name,
        "dob": dob,
        "age": int(age) if age else None,
        "phone": phone,
        "email": email,
    }

    try:
        supabase.table("users").insert(payload).execute()
    except Exception as e:
        return render_template("signup.html", error="Insert failed: " + str(e))

    return redirect("/login")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------------------------------------------------
# API — USER PROFILE
# ---------------------------------------------------------
@app.route("/api/me")
def api_me():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401

    uid = session.get("user_id")
    res = supabase.table("users").select("*").eq("id", uid).single().execute()

    if not res.data:
        return jsonify({"error": "User not found"}), 404

    user = res.data
    user.pop("password_hash", None)
    return jsonify({"user": user})


# ---------------------------------------------------------
# API — APPOINTMENTS
# ---------------------------------------------------------

@app.route("/api/my-appointments")
def api_my_appointments():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401

    uid = session.get("user_id")
    res = supabase.table("appointments").select("*").eq("user_id", uid).execute()

    return jsonify({"appointments": res.data or []})


@app.route("/api/appointments", methods=["POST"])
def api_create_appointment():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json() or request.form
    doctor = data.get("doctor_name")
    specialty = data.get("specialty", "General")
    date = data.get("date")
    time = data.get("time")
    notes = data.get("notes", "")

    if not doctor or not date or not time:
        return jsonify({"error": "Missing fields"}), 400

    payload = {
        "user_id": session.get("user_id"),
        "doctor_name": doctor,
        "specialty": specialty,
        "date": date,
        "time": time,
        "notes": notes,
    }

    res = supabase.table("appointments").insert(payload).execute()

    return jsonify({"success": True, "appointment": res.data[0]})


@app.route("/api/appointments/<appt_id>", methods=["DELETE"])
def api_delete_appointment(appt_id):
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401

    uid = session.get("user_id")

    # Verify user owns this appointment
    check = supabase.table("appointments").select("id").eq("id", appt_id).eq("user_id", uid).execute()
    if not check.data:
        return jsonify({"error": "Not found"}), 404

    supabase.table("appointments").delete().eq("id", appt_id).execute()
    return jsonify({"success": True})


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 App running at http://localhost:3000")
    app.run(debug=True, port=3000)
