import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time

st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

# Visual Engine: Neon Sunset Mesh with Explicit Dark Dropdown Select Text Rules
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(135deg, rgba(99, 102, 241, 0.72) 0%, rgba(244, 63, 94, 0.75) 50%, rgba(15, 23, 42, 0.92) 100%), 
                          url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-title { font-family: sans-serif; font-size: 28px !important; font-weight: 900; color: #FFFFFF; text-shadow: 0px 4px 10px rgba(0,0,0,0.5); margin-bottom: 5px; }
    label, p, span, h2, h4 { color: #FFFFFF !important; font-weight: 600; text-shadow: 0px 2px 4px rgba(0,0,0,0.4); }
    
    /* Semi-Transparent Input Containers */
    div[data-baseweb="select"], div[data-baseweb="base-input"] { background: rgba(15, 23, 42, 0.55) !important; backdrop-filter: blur(8px); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.15) !important; }
    
    /* FIXED: Explicitly force selectbox inner text values and choice items to dark charcoal for maximum contrast */
    div[data-baseweb="select"] [data-user-value="true"], 
    div[role="listbox"] li, 
    .stSelectbox div[data-baseweb="select"] span { 
        color: #0F172A !important; 
        font-weight: 700 !important; 
    }
    
    /* Target multiselect chip labels to remain bright white against their dark chips */
    div[data-baseweb="tag"] span { color: #FFFFFF !important; }
    
    /* High-Vibe Button Styling */
    div.stButton > button { width: 100%; background: linear-gradient(90deg, #6366F1, #EC4899) !important; color: white !important; border-radius: 14px; font-weight: 800; padding: 14px; border: none !important; box-shadow: 0px 4px 15px rgba(236, 72, 153, 0.4); }
    .admin-btn > div.stButton > button { background: linear-gradient(90deg, #EF4444, #DC2626) !important; box-shadow: 0px 4px 12px rgba(239, 68, 68, 0.4); }
    .back-btn > div.stButton > button { background: rgba(30, 41, 59, 0.8) !important; border: 1px solid rgba(255,255,255,0.2) !important; margin-top: 15px; box-shadow: none; }
    .exit-admin-btn > div.stButton > button { background: rgba(15, 23, 42, 0.9) !important; border: 1px solid rgba(255,255,255,0.1) !important; margin-top: 10px; color: #E2E8F0 !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(15, 23, 42, 0.6) !important; backdrop-filter: blur(4px); border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px 10px 0px 0px; padding: 12px 24px !important; color: #CBD5E1 !important; font-weight: 700; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366F1, #4F46E5) !important; color: white !important; border-color: #6366F1 !important; box-shadow: 0px 4px 10px rgba(99, 102, 241, 0.3); }
    
    /* Neon Status Badge System */
    .neon-badge { display: inline-block; padding: 6px 14px; font-size: 11px; font-weight: 900; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; text-shadow: none !important; }
    .badge-driver { background-color: rgba(34, 197, 94, 0.25); color: #4ADE80; border: 1px solid #22C55E; box-shadow: 0 0 12px rgba(34,197,94,0.4); }
    .badge-full { background-color: rgba(56, 189, 248, 0.25); color: #38BDF8; border: 1px solid #0EA5E9; box-shadow: 0 0 12px rgba(56,189,248,0.4); }
    .badge-half { background-color: rgba(251, 191, 36, 0.25); color: #FBBF24; border: 1px solid #D97706; box-shadow: 0 0 12px rgba(251,191,36,0.4); }
    .badge-holiday { background-color: rgba(168, 85, 247, 0.25); color: #C084FC; border: 1px solid #9333EA; }
    
    .lock-banner { background-color: rgba(15, 23, 42, 0.75); backdrop-filter: blur(12px); border: 2px solid #EF4444; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
    .future-banner { background-color: rgba(15, 23, 42, 0.75); backdrop-filter: blur(12px); border: 2px solid #EAB308; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(234, 179, 8, 0.3); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">🌅 MG Carpool Hub</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

if "holiday_list" not in st.session_state: st.session_state.holiday_list = []
if "just_saved" not in st.session_state: st.session_state.just_saved = False
if "saved_message" not in st.session_state: st.session_state.saved_message = ""
if "last_processed_date" not in st.session_state: st.session_state.last_processed_date = None
if "disable_lock" not in st.session_state: st.session_state.disable_lock = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False

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
        st.markdown("""
            <div class="future-banner">
                <span style="font-size: 45px;">🔮</span>
                <h2 style="color: #EAB308; margin-top: 10px; font-weight:800; font-family:sans-serif;">Ye kam bhi Loudu ka hi hai</h2>
                <h4 style="color: #F8FAFC; font-weight: 700; margin-top: 5px;">You cannot log entries for future dates.</h4>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙 GO BACK TO TODAY", key="future_back_btn"):
            st.query_params["reset"] = "true"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.just_saved:
        st.success(st.session_state.saved_message)
        st.session_state.just_saved = False
        time.sleep(2.0)
        st.rerun()

    elif date_exists and not st.session_state.is_admin and not st.session_state.disable_lock:
        st.error("🚨 ACCESS RESTRICTED FOR THIS DATE")
        st.markdown(f"""
            <div class="lock-banner">
                <span style="font-size: 45px;">🛑</span>
                <h2 style="color: #EF4444; margin-top: 10px; font-weight:900; font-family:sans-serif; letter-spacing: 0.5px;">Abe Loudu dubara kyun kar raha!</h2>
                <h4 style="margin: 12px 0 0 0; color: #F8FAFC; font-weight: 700;">Ab mantri karega Sahi.</h4>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="back
