import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io

st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.95)), 
                          url('https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=800&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-title { font-family: sans-serif; font-size: 26px !important; font-weight: 800; color: #FFFFFF; }
    label, p, span { color: #CBD5E1 !important; }
    div.stButton > button { width: 100%; background-color: #6366F1 !important; color: white !important; border-radius: 12px; font-weight: 700; padding: 12px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">📝 Log Daily Commute</p>', unsafe_allow_html=True)

commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]

# API configuration helpers
TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Fetch shared file from GitHub Repo Cloud Storage
@st.cache_data(ttl=5)
def load_global_csv():
    if not TOKEN or not REPO: return pd.DataFrame()
    r = requests.get(URL, headers=HEADERS)
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode("utf-8")
        return pd.read_csv(io.StringIO(content))
    return pd.DataFrame()

df_existing = load_global_csv()

travel_date = st.date_input("Date of Travel", datetime.date.today())
driver = st.selectbox("Designated Driver", commuters)
passenger_options = [c for c in commuters if c != driver]
full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options)
remaining_options = [p for p in passenger_options if p not in full_day]
half_day = st.multiselect("Half-Day Passengers (₹150)", remaining_options)

if st.button("💾 SAVE TRIP TO LEDGER"):
    if not TOKEN or not REPO:
        st.error("Setup Incomplete: Please add GITHUB_TOKEN and GITHUB_REPO keys into your App Secrets configurations pane.")
        st.stop()
        
    full_day_str = ", ".join(full_day) if full_day else "None"
    half_day_str = ", ".join(half_day) if half_day else "None"
    
    new_row = pd.DataFrame([{"Date": str(travel_date), "Driver": driver, "Full Day Passengers": full_day_str, "Half Day Passengers": half_day_str}])
    
    if not df_existing.empty:
        df_existing = df_existing[df_existing["Date"].astype(str) != str(travel_date)]
        df_final = pd.concat([df_existing, new_row], ignore_index=True)
    else:
        df_final = new_row
        
    csv_buffers = df_final.to_csv(index=False)
    
    # Get file sha metadata if it already exists to overwrite cleanly
    r_exist = requests.get(URL, headers=HEADERS)
    sha = r_exist.json()["sha"] if r_exist.status_code == 200 else None
    
    payload = {
        "message": f"Update carpool records for {travel_date}",
        "content": base64.b64encode(csv_buffers.encode("utf-8")).decode("utf-8")
    }
    if sha: payload["sha"] = sha
        
    r_put = requests.put(URL, headers=HEADERS, json=payload)
    if r_put.status_code in [200, 201]:
        st.success(f"🎉 Trip successfully pushed globally for {travel_date.strftime('%d %b')}!")
        st.cache_data.clear()
    else:
        st.error(f"Write update rejection failure: {r_put.text}")
