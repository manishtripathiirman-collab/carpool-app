import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random

st.set_page_config(page_title="MG Logger", page_icon="🚗", layout="centered")

# Visual Engine: Dark Modern Core Layout
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0F172A !important;
    }
    .block-container {
        background: rgba(30, 41, 59, 0.7) !important;
        padding: 25px !important; 
        border-radius: 20px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5) !important; 
        margin-top: 20px !important;
    }
    .mobile-title { font-family: sans-serif; font-size: 28px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 20px; }
    label, p, span, h2, h3, h4 { color: #F1F5F9 !important; font-weight: 700 !important; }
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
    .lock-banner { background-color: #0F172A; border: 2px solid #EF4444; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0px 0px 20px rgba(239, 68, 68, 0.3); }
    .future-banner { background-color: #0F172A; border: 2px solid #EAB308; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0px 0px 20px rgba(234, 179, 8, 0.3); }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="mobile-title">🌅 MG Carpool Hub</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

if "just_saved" not in st.session_state: st.session_state.just_saved = False
if "saved_message" not in st.session_state: st.session_state.saved_message = ""
if "is_admin" not in st.session_state: st.session_state.is_admin = False

# Hard-anchored Indian Standard Time
utc_now = datetime.datetime.utcnow()
ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
today_date_ist = ist_now.date()

# PULL PURELY FROM THE STREAMLIT SECRETS VAULT
TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache"
}

TRIP_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"

df_existing = pd.DataFrame()

if TOKEN and REPO:
    try:
        r = requests.get(f"{TRIP_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r.status_code == 200:
            df_existing = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
    except Exception:
        pass

travel_date = st.date_input("Date of Travel", today_date_ist, key="trip_date_norm")

is_future_date = travel_date > today_date_ist

date_exists = False
if not df_existing.empty and "Date" in df_existing.columns:
    target_dash = travel_date.strftime("%Y-%m-%d").strip()
    target_slash = travel_date.strftime("%Y/%m/%d").strip()
    df_existing["Cleaned_Date_Str"] = df_existing["Date"].astype(str).str.strip()
    date_exists = (target_dash in df_existing["Cleaned_Date_Str"].values) or (target_slash in df_existing["Cleaned_Date_Str"].values)

if is_future_date:
    st.markdown("<div class='future-banner'><h1 style='font-size:50px;margin:0;'>🔮</h1><h2 style='font-size:32px;color:#EAB308;font-weight:900;margin:10px 0;'>Ye kam bhi Loudu ka hi hai</h2><h4 style='font-size:18px;color:#F1F5F9;font-weight:700;'>You cannot log entries for future dates.</h4></div>", unsafe_allow_html=True)

elif st.session_state.just_saved:
    st.success(st.session_state.saved_message)
    st.session_state.just_saved = False
    time.sleep(1.5)
    st.rerun()

# NO OVERRIDE LOGIC: Shows warning banner to normal users, locks out fields completely
elif date_exists and not st.session_state.is_admin:
    st.markdown("<div class='lock-banner'><h1 style='font-size:50px;margin:0;'>🛑</h1><h2 style='font-size:32px;color:#EF4444;font-weight:900;margin:10px 0;'>Abe Loudu dubara kyun kar raha!</h2><h4 style='font-size:18px;color:#F1F5F9;font-weight:700;'>Ab mantri karega Sahi.</h4></div>", unsafe_allow_html=True)

else:
    driver = st.selectbox("Designated Driver", all_commuters, key="driver_select_box")
    passenger_options = [c for c in all_commuters if c != driver]
    
    full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options, key="full_select_box")
    half_day = st.multiselect("Half-Day Passengers (₹150)", [p for p in passenger_options if p not in full_day], key="half_select_box")

    if st.button("💾 SAVE TRIP TO LEDGER"):
        if date_exists and not st.session_state.is_admin:
            st.error("🛑 Lock active: Overriding entries is prohibited!")
        else:
            full_str = ", ".join(full_day) if full_day else "None"
            half_str = ", ".join(half_day) if half_day else "None"
            
            new_row = pd.DataFrame([{"Date": str(travel_date), "Driver": driver, "Full Day Passengers": full_str, "Half Day Passengers": half_str}])
            
            # Admin Mode cleaner: replaces existing entry line flawlessly
            if date_exists and st.session_state.is_admin and not df_existing.empty:
                df_final = df_existing[~df_existing["Cleaned_Date_Str"].isin([str(travel_date)])]
                df_final = pd.concat([df_final, new_row], ignore_index=True)
            else:
                df_final = pd.concat([df_existing, new_row], ignore_index=True) if not df_existing.empty else new_row
            
            if "Cleaned_Date_Str" in df_final.columns: 
                df_final = df_final.drop(columns=["Cleaned_Date_Str"])
            
            payload = {"message": f"Log commute {travel_date}", "content": base64.b64encode(df_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
            
            r_sha = requests.get(f"{TRIP_URL}?getsha={random.randint(1, 1000000)}", headers=HEADERS)
            if r_sha.status_code == 200: 
                payload["sha"] = r_sha.json()["sha"]
            
            res_put = requests.put(TRIP_URL, headers=HEADERS, json=payload)
            if res_put.status_code in [200, 201]:
                st.toast("Saved successfully!", icon="✅")
                st.session_state.just_saved = True
                st.session_state.saved_message = f"🎉 Trip saved cleanly to ledger!"
                st.rerun()
            else:
                st.error("🛑 Sync Failure: Token in Streamlit Secrets is invalid or expired.")

st.markdown("---")
with st.expander("🛠️ Admin Controls"):
    if not st.session_state.is_admin:
        admin_pin = st.text_input("Enter Admin PIN", type="password", key="pin_field")
        if admin_pin == "9999":
            st.session_state.is_admin = True
            st.rerun()
    else:
        st.success("👑 Admin Mode Active (Override Enabled)")
        if st.button("🔙 EXIT ADMIN MODE"):
            st.session_state.is_admin = False
            st.rerun()
