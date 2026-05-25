import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random

st.set_page_config(page_title="MG Logger", page_icon="🚗", layout="centered")

# Visual Engine: Pure Dark Layout with Fixed Text Target Selectors
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0F172A !important;
        overflow-y: auto !important;
    }
    .block-container {
        background: rgba(30, 41, 59, 0.7) !important;
        padding: 25px !important; 
        border-radius: 20px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5) !important; 
        margin-top: 35px !important;
        margin-bottom: 30px !important;
    }
    .mobile-title { font-family: sans-serif; font-size: 24px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 20px; }
    
    div[data-testid="stWidgetLabel"] p, 
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stTab"] p,
    .block-container h2, .block-container h3, .block-container h4 { 
        color: #F1F5F9 !important; 
        font-weight: 700 !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    
    div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div { 
        background-color: #1E293B !important; border-radius: 10px !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; 
    }
    div[data-baseweb="select"] [data-user-value="true"], .stSelectbox div [data-baseweb="select"] span, div[data-baseweb="base-input"] input { 
        color: #FFFFFF !important; font-weight: 700 !important; 
    }
    div[role="listbox"] { background-color: #1E293B !important; border: 1px solid rgba(255,255,255,0.2) !important; }
    div[role="listbox"] li { color: #FFFFFF !important; font-weight: 700 !important; }
    div[role="listbox"] li:hover { background-color: #334155 !important; }
    div[data-baseweb="tag"] { background-color: #334155 !important; border-radius: 6px; }
    div[data-baseweb="tag"] span { color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 8px 8px 0px 0px; padding: 10px 20px !important; color: #94A3B8 !important; font-weight: 700; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366F1, #4F46E5) !important; color: white !important; border-color: #6366F1 !important; }
    div.stButton > button { width: 100%; background: linear-gradient(90deg, #6366F1, #EC4899) !important; color: white !important; border-radius: 12px; font-weight: 800; padding: 14px; border: none !important; box-shadow: 0px 4px 15px rgba(236, 72, 153, 0.3); }
    .admin-btn > div.stButton > button { background: linear-gradient(90deg, #EF4444, #DC2626) !important; box-shadow: 0px 4px 12px rgba(239, 68, 68, 0.3); }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="mobile-title">🌅 MG Carpool Hub - <span style="font-size: 10px; font-weight: 400; color: #64748B; text-transform: lowercase; vertical-align: middle;">mantri</span></p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

# Time calculations
utc_now = datetime.datetime.utcnow()
ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
today_date_ist = ist_now.date()

# State Engine Initialization
if "holiday_list" not in st.session_state: st.session_state.holiday_list = []
if "just_saved" not in st.session_state: st.session_state.just_saved = False
if "just_saved_exp" not in st.session_state: st.session_state.just_saved_exp = False
if "saved_message" not in st.session_state: st.session_state.saved_message = ""
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "reset_trigger" not in st.session_state: st.session_state["reset_trigger"] = 0

# Persistent Validation Trigger Flags
if "trip_error_flag" not in st.session_state: st.session_state.trip_error_flag = None
if "exp_error_flag" not in st.session_state: st.session_state.exp_error_flag = None

TOKEN = st.secrets.get("GITHUB_TOKEN", "").strip()
REPO = st.secrets.get("GITHUB_REPO", "").strip()

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache"
}

TRIP_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
EXPENSE_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

df_existing = pd.DataFrame()
df_exp_existing = pd.DataFrame()

if TOKEN and REPO:
    try:
        r = requests.get(f"{TRIP_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r.status_code == 200:
            df_existing = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
        
        r_e = requests.get(f"{EXPENSE_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r_e.status_code == 200:
            df_exp_existing = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))
    except Exception:
        pass

tab_trip, tab_expense = st.tabs(["🚗 Log Commute", "💰 Split Expenses"])

with tab_trip:
    travel_date = st.date_input(
        "Date of Travel", 
        today_date_ist, 
        key=f"trip_date_picker_bound_{st.session_state['reset_trigger']}"
    )

    # Clear validation state immediately when the travel date drops change
    if 'last_travel_date' not in st.session_state or st.session_state.last_travel_date != str(travel_date):
        st.session_state.trip_error_flag = None
        st.session_state.last_travel_date = str(travel_date)

    is_future_date = travel_date > today_date_ist
    
    date_exists = False
    if not df_existing.empty and "Date" in df_existing.columns:
        t_dash = travel_date.strftime("%Y-%m-%d").strip()
        t_slash = travel_date.strftime("%Y/%m/%d").strip()
        df_existing["Cleaned_Date_Str"] = df_existing["Date"].astype(str).str.strip()
        date_exists = (t_dash in df_existing["Cleaned_Date_Str"].values) or (t_slash in df_existing["Cleaned_Date_Str"].values)

    if st.session_state.just_saved:
        st.success(st.session_state.saved_message)
        st.session_state.just_saved = False
        time.sleep(1.5)
        st.rerun()

    commuters = [c for c in all_commuters if c not in st.session_state.holiday_list]
    if not commuters: commuters = all_commuters

    driver = st.selectbox("Designated Driver", commuters, key="driver_select_box")
    passenger_options = [c for c in commuters if c != driver]
    full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options, key="full_select_box")
    half_day = st.multiselect("Half-Day Passengers (₹150)", [p for p in passenger_options if p not in full_day], key="half_select_box")

    if st.session_state.trip_error_flag == "future":
        st.error("🔮 Ye kam bhi Loudu ka hi hai. You cannot log entries for future dates.")
        if st.button("🔙 RESET TRAVEL DATE", key="reset_trip_future_btn"):
            st.session_state.trip_error_flag = None
            st.session_state["reset_trigger"] += 1
            st.rerun()
    elif st.session_state.trip_error_flag == "duplicate":
        st.warning("🛑 Abe Loudu dubara kyun kar raha! Ab mantri karega Sahi. Use Admin Suite below to adjust fields.")
        if st.button("🔙 CHANGE SELECTION DATE", key="reset_trip_dup_btn"):
            st.session_state.trip_error_flag = None
            st.session_state["reset_trigger"] += 1
            st.rerun()

    if st.button("💾 SAVE TRIP TO LEDGER", key="save_trip_ledger_btn"):
        if is_future_date:
            st.session_state.trip_error_flag = "future"
            st.rerun()
        elif date_exists and not st.session_state.is_admin:
            st.session_state.trip_error_flag = "duplicate"
            st.rerun()
        else:
            st.session_state.trip_error_flag = None
            with st.spinner("Saving commute parameters..."):
                full_str = ", ".join([p.strip().title() for p in full_day]) if full_day else "None"
                half_str = ", ".join([p.strip().title() for p in half_day]) if half_day else "None"
                
                new_row = pd.DataFrame([{"Date": str(travel_date), "Driver": driver.strip().title(), "Full Day Passengers": full_str, "Half Day Passengers": half_str}])
                
                if date_exists and st.session_state.is_admin and not df_existing.empty:
                    t_dash = travel_date.strftime("%Y-%m-%d").strip()
                    t_slash = travel_date.strftime("%Y/%m/%d").strip()
                    df_cleaned_base = df_existing[(df_existing["Cleaned_Date_Str"] != t_dash) & (df_existing["Cleaned_Date_Str"] != t_slash)]
                    df_final = pd.concat([df_cleaned_base, new_row], ignore_index=True)
                else:
                    df_final = pd.concat(
