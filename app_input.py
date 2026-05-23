import streamlit as st
import datetime
import pandas as pd

# --- MOBILE WINDOW CONFIGURATION ---
st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

# --- AMBIENT DARK AUTOMOTIVE THEME ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.95)), 
                          url('https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=800&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-title {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 26px !important; font-weight: 800; color: #FFFFFF;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
    }
    label, p, span { color: #CBD5E1 !important; }
    div.stButton > button { 
        width: 100%; background-color: #6366F1 !important; 
        color: white !important; border-radius: 12px; font-weight: 700; padding: 12px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">📝 Log Daily Commute</p>', unsafe_allow_html=True)
st.caption("Select today's travel details to update the permanent group database.")

# --- CORE MEMBERS ---
commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]

# --- LOCAL DATABASE FILE SETUP ---
# To keep things incredibly simple and bypass external connection issues online, 
# this app will save your entries to a shared, permanent file right inside your workspace.
DATA_FILE = "carpool_logs.csv"

# Load existing data if it exists so we don't lose history when the app restarts
if "trip_history" not in st.session_state:
    if pd.io.common.file_exists(DATA_FILE):
        st.session_state.trip_history = pd.read_csv(DATA_FILE).to_dict(orient="records")
    else:
        st.session_state.trip_history = []

# --- SMART INPUT FIELDS ---
travel_date = st.date_input("Date of Travel", datetime.date.today())
driver = st.selectbox("Designated Driver", commuters)

# Filter out the driver so they cannot accidentally be marked as a passenger
passenger_options = [c for c in commuters if c != driver]

full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options)

# Filter out full-day passengers so they can't be selected for half-day
remaining_options = [p for p in passenger_options if p not in full_day]
half_day = st.multiselect("Half-Day Passengers — AM/PM (₹150)", remaining_options)

# --- SAVE ACTION ---
if st.button("💾 SAVE TRIP TO LEDGER"):
    # Format selected passengers into text lists
    full_day_str = ", ".join(full_day) if full_day else "None"
    half_day_str = ", ".join(half_day) if half_day else "None"
    
    # Remove any existing entry for this exact date to allow clean overwrites/edits
    st.session_state.trip_history = [t for t in st.session_state.trip_history if t["Date"] != str(travel_date)]
    
    # Append the new entry
    st.session_state.trip_history.append({
        "Date": str(travel_date),
        "Driver": driver,
        "Full Day Passengers": full_day_str,
        "Half Day Passengers": half_day_str
    })
    
    # Save permanently to the cloud workspace file
    pd.DataFrame(st.session_state.trip_history).to_csv(DATA_FILE, index=False)
    st.success(f"🎉 Trip successfully saved for {travel_date.strftime('%d %b')}!")

# --- VIEW RECENT HISTORY ---
if st.session_state.trip_history:
    with st.expander("📊 View Saved Logs in This Session", expanded=False):
        st.dataframe(pd.DataFrame(st.session_state.trip_history), use_container_width=True, hide_index=True)
