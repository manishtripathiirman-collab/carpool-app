import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time

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
    .admin-btn > div.stButton > button { background-color: #EF4444 !important; }
    .back-btn > div.stButton > button { background-color: #475569 !important; border: 1px solid #64748B !important; margin-top: 15px; }
    .exit-admin-btn > div.stButton > button { background-color: #1E293B !important; border: 1px solid #334155 !important; margin-top: 10px; color: #94A3B8 !important; }
    
    .lock-banner { 
        background-color: rgba(239, 68, 68, 0.2); 
        border: 2px solid #EF4444; 
        padding: 25px; 
        border-radius: 16px; 
        text-align: center; 
        margin-bottom: 20px;
        animation: pulse 1.5s infinite;
    }
    .future-banner {
        background-color: rgba(234, 179, 8, 0.15); 
        border: 2px solid #EAB308; 
        padding: 25px; 
        border-radius: 16px; 
        text-align: center; 
        margin-bottom: 20px;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
        50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.7); border-color: #F87171; }
        100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">📝 Log Daily Commute</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

if "holiday_list" not in st.session_state:
    st.session_state.holiday_list = []
if "just_saved" not in st.session_state:
    st.session_state.just_saved = False
if "saved_message" not in st.session_state:
    st.session_state.saved_message = ""
if "last_processed_date" not in st.session_state:
    st.session_state.last_processed_date = None
if "disable_lock" not in st.session_state:
    st.session_state.disable_lock = False
if "admin_pin_input" not in st.session_state:
    st.session_state.admin_pin_input = ""

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

live_url = f"{URL}?timestamp={datetime.datetime.now().timestamp()}"
df_existing = pd.DataFrame()

if TOKEN and REPO:
    r = requests.get(live_url, headers=HEADERS)
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode("utf-8")
        df_existing = pd.read_csv(io.StringIO(content))

# Date picker handling
if "reset" in st.query_params:
    st.query_params.clear()
    travel_date = st.date_input("Date of Travel", datetime.date.today())
else:
    travel_date = st.date_input("Date of Travel", datetime.date.today())

# Track date adjustments
if st.session_state.last_processed_date != str(travel_date):
    st.session_state.disable_lock = False
    st.session_state.last_processed_date = str(travel_date)

# Evaluated Date Logic Boundaries
today_date = datetime.date.today()
is_future_date = travel_date > today_date

date_exists = False
if not df_existing.empty and not is_future_date:
    date_exists = str(travel_date) in df_existing["Date"].astype(str).values

is_admin_authenticated = False

# --- EXPANDER CONTROLS AT THE BOTTOM ---
st.markdown("---")
if not df_existing.empty:
    total_days = len(df_existing)
    st.markdown(f"📊 **Total Logged Days in Database:** `{total_days} Days`")
    with st.expander("👁️ View All Logged Days", expanded=False):
        st.dataframe(df_existing.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🛠️ Admin Controls (Authorized Only)"):
        admin_pin = st.text_input("Enter Admin PIN to Unlock / Delete", type="password", value=st.session_state.admin_pin_input, key="admin_pin_field")
        
        if admin_pin == "9999":
            st.success("Access Granted: Master Controls Unlocked")
            is_admin_authenticated = True
            
            st.markdown('<div class="exit-admin-btn">', unsafe_allow_html=True)
            if st.button("🔙 EXIT ADMIN MODE"):
                st.session_state.admin_pin_input = ""
                st.query_params["reset"] = "true"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
            
            st.markdown("#### 🌴 Skip This Person (Active Holiday Matrix)")
            selected_holidays = []
            cols = st.columns(len(all_commuters))
            for idx, person in enumerate(all_commuters):
                with cols[idx]:
                    is_away = st.checkbox(person, value=(person in st.session_state.holiday_list))
                    if is_away:
                        selected_holidays.append(person)
            
            if sorted(selected_holidays) != sorted(st.session_state.holiday_list):
                st.session_state.holiday_list = selected_holidays
                st.rerun()
                
            st.markdown("---")
            st.markdown("#### 🗑️ Delete Ledger Records")
            delete_date = st.selectbox("Select Date to Delete completely:", sorted(df_existing["Date"].unique(), reverse=True))
            
            st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
            if st.button("🗑️ PERMANENTLY DELETE CHOSEN DATE"):
                df_final = df_existing
