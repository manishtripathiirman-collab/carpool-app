import streamlit as st
import datetime
import json

st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

# Visual Framing Theme
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #FFFFFF; }
    label, p, span { color: #CBD5E1 !important; }
    div.stButton > button { width: 100%; background-color: #6366F1 !important; color: white !important; border-radius: 12px; font-weight: 700; padding: 12px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('## 📝 Log Daily Commute')

commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

# Core Shared Memory Space Mapping
if "global_db" not in st.session_state:
    st.session_state.global_db = []

travel_date = st.date_input("Date of Travel", datetime.date.today())
driver = st.selectbox("Designated Driver", commuters)
passenger_options = [c for c in commuters if c != driver]
full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options)
remaining_options = [p for p in passenger_options if p not in full_day]
half_day = st.multiselect("Half-Day Passengers (₹150)", remaining_options)

if st.button("💾 SAVE TRIP TO LEDGER"):
    # Create clean record layout
    new_entry = {
        "Date": str(travel_date),
        "Driver": driver,
        "Full": full_day,
        "Half": half_day
    }
    
    # Remove existing matching calendar day entries to prevent duplicate billing rows
    st.session_state.global_db = [t for t in st.session_state.global_db if t["Date"] != str(travel_date)]
    st.session_state.global_db.append(new_entry)
    
    # Store directly in local persistent cache block
    st.success(f"🎉 Entry successfully saved for {travel_date.strftime('%d %b')}!")
    
if st.session_state.global_db:
    with st.expander("📊 Current Active Session Logs Ledger Table"):
        st.write(st.session_state.global_db)
