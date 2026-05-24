import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time

st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

# Visual Engine: Neon Style Sheet Injection with Vibrant Retro Sunset Drive Backdrop
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.94)), 
                          url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-title { font-family: sans-serif; font-size: 26px !important; font-weight: 800; color: #FFFFFF; margin-bottom: 0px; }
    label, p, span, h2, h4 { color: #CBD5E1 !important; }
    div.stButton > button { width: 100%; background-color: #6366F1 !important; color: white !important; border-radius: 12px; font-weight: 700; padding: 12px; }
    .admin-btn > div.stButton > button { background-color: #EF4444 !important; }
    .back-btn > div.stButton > button { background-color: #475569 !important; border: 1px solid #64748B !important; margin-top: 15px; }
    .exit-admin-btn > div.stButton > button { background-color: #1E293B !important; border: 1px solid #334155 !important; margin-top: 10px; color: #94A3B8 !important; color: #94A3B8 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(30, 41, 59, 0.7) !important; border: 1px solid #334155 !important; border-radius: 8px 8px 0px 0px; padding: 10px 20px !important; color: #94A3B8 !important; }
    .stTabs [aria-selected="true"] { background-color: #6366F1 !important; color: white !important; border-color: #6366F1 !important; }
    
    .neon-badge { display: inline-block; padding: 5px 12px; font-size: 11px; font-weight: 800; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .badge-driver { background-color: rgba(34, 197, 94, 0.15); color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.4); animation: pulse-green 2s infinite alternate; }
    .badge-full { background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4); animation: pulse-blue 2s infinite alternate; }
    .badge-half { background-color: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.4); animation: pulse-amber 2s infinite alternate; }
    .badge-holiday { background-color: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.4); }
    
    @keyframes pulse-green { 0% { box-shadow: 0 0 4px rgba(34,197,94,0.2); } 100% { box-shadow: 0 0 12px rgba(34,197,94,0.6); border-color: #22C55E; } }
    @keyframes pulse-blue { 0% { box-shadow: 0 0 4px rgba(56,189,248,0.2); } 100% { box-shadow: 0 0 12px rgba(56,189,248,0.6); border-color: #38BDF8; } }
    @keyframes pulse-amber { 0% { box-shadow: 0 0 4px rgba(251,191,36,0.2); } 100% { box-shadow: 0 0 12px rgba(251,191,36,0.6); border-color: #FBBF24; } }
    
    .lock-banner { background-color: rgba(239, 68, 68, 0.2); border: 2px solid #EF4444; padding: 25px; border-radius: 16px; text-align: center; margin-bottom: 20px; animation: pulse-red 1.5s infinite; }
    @keyframes pulse-red { 0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); } 50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.7); border-color: #F87171; } 100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); } }
    .future-banner { background-color: rgba(234, 179, 8, 0.15); border: 2px solid #EAB308; padding: 25px; border-radius: 16px; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">📝 MG Carpool Hub</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

if "holiday_list" not in st.session_state: st.session_state.holiday_list = []
if "just_saved" not in st.session_state: st.session_state.just_saved = False
if "saved_message" not in st.session_state: st.session_state.saved_message = ""
if "last_processed_date" not in st.session_state: st.session_state.last_processed_date = None
if "disable_lock" not in st.session_state: st.session_state.disable_lock = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False

# Dynamic Indian Standard Time (+5.5 Hours) Calculator Engine
utc_now = datetime.datetime.utcnow()
ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
today_date_ist = ist_now.date()

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

TRIP_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
EXPENSE_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

df_existing = pd.DataFrame()
df_exp_existing = pd.DataFrame()

if TOKEN and REPO:
    r = requests.get(f"{TRIP_URL}?ts={time.time()}", headers=HEADERS)
    if r.status_code == 200:
        df_existing = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
    r_e = requests.get(f"{EXPENSE_URL}?ts={time.time()}", headers=HEADERS)
    if r_e.status_code == 200:
        df_exp_existing = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))

# FIXED: Re-anchored the layout tab selection assignment sequence completely
tab_trip, tab_expense = st.tabs(["🚗 Log Commute", "💰 Split Expenses"])

# TAB 1: COMMUTE LOGGING
with tab_trip:
    if "reset" in st.query_params:
        st.query_params.clear()
        travel_date = st.date_input("Date of Travel", today_date_ist, key="trip_date_reset")
    else:
        travel_date = st.date_input("Date of Travel", today_date_ist, key="trip_date_norm")

    if st.session_state.last_processed_date != str(travel_date):
        st.session_state.disable_lock = False
        st.session_state.last_processed_date = str(travel_date)

    is_future_date = travel_date > today_date_ist
    date_exists = str(travel_date) in df_existing["Date"].astype(str).values if not df_existing.empty else False

    if is_future_date:
        st.warning("⏳ FUTURE TRIPS NOT ALLOWED")
        st.markdown('<div class="future-banner"><span style="font-size: 45px;">🔮</span><h2 style="color: #EAB308; margin-top: 10px; font-weight:800; font-family:sans-serif;">Ye kam bhi Loudu ka hi hai</h2><h4 style="color: #F8FAFC; font-weight: 700; margin-top: 5px;">You cannot log entries for future dates.</h4></div>', unsafe_allow_html=True)
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙 GO BACK TO TODAY", key="future_back_btn"):
            st.query_params["reset"] = "true"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=
