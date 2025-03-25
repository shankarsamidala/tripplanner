import streamlit as st
import sqlite3
import hashlib
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyD8_9xLSB7YoVOBtVDSBJcjKAP_UpLW9kA")

# Database setup
def create_db():
    conn = sqlite3.connect("travel_planner.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    conn.commit()
    conn.close()

create_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect("travel_planner.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = sqlite3.connect("travel_planner.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def generate_trip_plan(from_location, destination, num_people, num_days, budget, preferences):
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    prompt = f"""
    You are a travel planner AI. Plan a {num_days}-day trip for {num_people} people from {from_location} to {destination}. 
    Budget: {budget}. Preferences: {preferences}.
    Provide a structured itinerary including transport, accommodation, activities, and food recommendations.
    """
    response = model.generate_content(prompt)
    return response.text

# Custom Styling
st.markdown("""
    <style>
        .main { background-color: #f0f2f6; }
        .stButton>button { width: 100%; border-radius: 8px; font-size: 16px; font-weight: bold; }
        .stTextInput, .stNumberInput, .stTextArea { border-radius: 8px; font-size: 14px; }
        .stTitle { color: #2c3e50; text-align: center; }
        .stSidebar {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 15px;
        }
        .stSidebar .stButton>button {
            background-color: #ff7e67;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
            transition: 0.3s;
        }
        .stSidebar .stButton>button:hover {
            background-color: #ff5b45;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🌍 Travel Planner")
st.sidebar.image("https://source.unsplash.com/400x250/?travel,adventure", use_column_width=True)
st.sidebar.markdown("### Plan your perfect trip with recommendations!")

if "user" not in st.session_state:
    if st.sidebar.button("🔑 Login"):
        st.session_state.page = "Login"
    if st.sidebar.button("📝 Signup"):
        st.session_state.page = "Signup"
else:
    if st.sidebar.button("🗺️ Plan Trip"):
        st.session_state.page = "Plan Trip"
    if st.sidebar.button("🚪 Logout"):
        del st.session_state["user"]
        st.session_state.page = "Login"
        st.rerun()

# Handle Pages
if "page" not in st.session_state:
    st.session_state.page = "Login"

if st.session_state.page == "Signup":
    st.title("🚀 Create a New Account")
    with st.form("signup_form"):
        new_user = st.text_input("👤 Username")
        new_password = st.text_input("🔒 Password", type="password")
        submit_button = st.form_submit_button("Sign Up")
        
        if submit_button:
            if register_user(new_user, new_password):
                st.success("🎉 Account created successfully! Please login.")
            else:
                st.error("⚠️ Username already exists. Try another.")

elif st.session_state.page == "Login":
    st.title("🔑 Login to Your Account")
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if login_user(username, password):
                st.session_state["user"] = username
                st.success(f"🎉 Welcome, {username}!")
                st.session_state.page = "Plan Trip"
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")

elif st.session_state.page == "Plan Trip":
    st.title("🗺️ Plan Your Dream Trip")
    with st.form("trip_form"):
        from_location = st.text_input("📍 From Location")
        destination = st.text_input("🏝️ Destination")
        num_people = st.number_input("👨‍👩‍👧‍👦 Number of People", min_value=1, step=1)
        num_days = st.number_input("📅 Number of Days", min_value=1, step=1)
        budget = st.text_input("💰 Budget (Low, Medium, High, or specific amount)")
        preferences = st.text_area("🎯 Special Preferences (Adventure, Relaxation, Family trip, etc.)")
        generate_button = st.form_submit_button("🚀 Generate Trip Plan")
        
        if generate_button:
            with st.spinner("⏳ Generating your trip plan..."):
                trip_plan = generate_trip_plan(from_location, destination, num_people, num_days, budget, preferences)
                st.session_state["trip_plan"] = trip_plan
                st.rerun()
    
    if "trip_plan" in st.session_state:
        st.subheader("🌟 Your Travel Itinerary")
        st.success(st.session_state["trip_plan"])
