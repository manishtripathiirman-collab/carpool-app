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

commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Fresh load directly from GitHub file storage
live_url = f"{URL}?timestamp={datetime.datetime.now().timestamp()}"
df_existing = pd.DataFrame()

if TOKEN and REPO:
    r = requests.get(live_url, headers=HEADERS)
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode("utf-8")
        df_existing = pd.read_csv(io.StringIO(content))

travel_date = st.date_input("Date of Travel", datetime.date.today())
driver = st.selectbox("Designated Driver", commuters)
passenger_options = [c for c in commuters if c != driver]
full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options)
remaining_options = [p for p in passenger_options if p not in full_day]
half_day = st.multiselect("Half-Day Passengers (₹150)", remaining_options)

if st.button("💾 SAVE TRIP TO LEDGER"):
    if not TOKEN or not REPO:
        st.error("Setup Incomplete in Secrets panel.")
        st.stop()
        
    full_day_str = ", ".join(full_day) if full_day else "None"
    half_day_str = ", ".join(half_day) if half_day else "None"
    
    new_row = pd.DataFrame([{"Date": str(travel_date), "Driver": driver, "Full Day Passengers": full_day_str, "Half Day Passengers": half_day_str}])
    
    if not df_existing.empty:
        df_cleaned = df_existing[df_existing["Date"].astype(str) != str(travel_date)]
        df_final = pd.concat([df_cleaned, new_row], ignore_index=True)
    else:
        df_final = new_row
        
    csv_buffers = df_final.to_csv(index=False)
    
    r_exist = requests.get(URL, headers=HEADERS)
    sha = r_exist.json()["sha"] if r_exist.status_code == 200 else None
    
    payload = {
        "message": f"Update carpool records for {travel_date}",
        "content": base64.b64encode(csv_buffers.encode("utf-8")).decode("utf-8")
    }
    if sha: payload["sha"] = sha
        
    r_put = requests.put(URL, headers=HEADERS, json=payload)
    if r_put.status_code in [200, 201]:
        st.success(f"🎉 Trip successfully saved for {travel_date.strftime('%d %b')}!")
        st.rerun()

# --- NEW: VISUAL HISTORY TRACKER IN INPUT APP ---
st.markdown("---")
if not df_existing.empty:
    total_days = len(df_existing)
    st.markdown(f"📊 **Total Logged Days in Database:** `{total_days} Days`")
    with st.expander("👁️ View All Logged Days", expanded=False):
        st.dataframe(df_existing.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("No logs found in the cloud database file yet.")
