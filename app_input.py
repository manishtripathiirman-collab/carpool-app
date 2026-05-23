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
        # Controlled value input to clear state safely via native script execution
        admin_pin = st.text_input("Enter Admin PIN to Unlock / Delete", type="password", value=st.session_state.admin_pin_input, key="admin_pin_field")
        
        if admin_pin == "9999":
            st.success("Access Granted: Master Controls Unlocked")
            is_admin_authenticated = True
            
            # EXIT ADMIN ACCESS NAVIGATION ELEMENT
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
                df_final = df_existing[df_existing["Date"].astype(str) != str(delete_date)]
                csv_buffers = df_final.to_csv(index=False)
                
                r_exist = requests.get(URL, headers=HEADERS)
                sha = r_exist.json()["sha"] if r_exist.status_code == 200 else None
                
                payload = {
                    "message": f"Admin delete records for {delete_date}",
                    "content": base64.b64encode(csv_buffers.encode("utf-8")).decode("utf-8"),
                    "sha": sha
                }
                
                r_put = requests.put(URL, headers=HEADERS, json=payload)
                if r_put.status_code in [200, 201]:
                    st.error(f"🗑️ Date {delete_date} has been completely wiped from ledger!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No logs found in the cloud database file yet.")

# --- RENDER CONDITIONAL ENTRY INTERFACE BASED ON LOCK STATUS ---
st.markdown("<br>", unsafe_allow_html=True)

# GATE 1: Trap Future Selections Immediately
if is_future_date:
    st.warning("⏳ FUTURE TRIPS NOT ALLOWED")
    st.markdown(f"""
        <div class="future-banner">
            <span style="font-size: 45px;">🔮</span>
            <h2 style="color: #EAB308; margin-top: 10px; font-weight:800; font-family:sans-serif;">Bhai, antaryami mat bano!</h2>
            <h4 style="color: #F8FAFC; font-weight: 700; margin-top: 5px;">You cannot log entries for future dates.</h4>
            <p style="margin: 15px 0 0 0; color: #94A3B8; font-size: 13px; font-style: italic;">[Selected: {travel_date.strftime('%d %b %Y')} - Please select a valid current or past date]</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("🔙 GO BACK TO TODAY", key="future_back_btn"):
        st.query_params["reset"] = "true"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# PRIORITY 1: Handle Success Intermission Display
elif st.session_state.just_saved:
    st.success(st.session_state.saved_message)
    st.session_state.just_saved = False
    st.session_state.saved_message = ""
    time.sleep(2.5)
    st.rerun()

# PRIORITY 2: Hard Lock Screen Check
elif date_exists and not is_admin_authenticated and not st.session_state.disable_lock:
    st.error("🚨 ACCESS RESTRICTED FOR THIS DATE")
    st.markdown(f"""
        <div class="lock-banner">
            <span style="font-size: 45px;">🛑</span>
            <h2 style="color: #EF4444; margin-top: 10px; font-weight:900; font-family:sans-serif; letter-spacing: 0.5px;">Abe Loudu dubara kyun kar raha!</h2>
            <h4 style="margin: 12px 0 0 0; color: #F8FAFC; font-weight: 700;">Ab mantri karega Sahi.</h4>
            <p style="margin: 18px 0 0 0; color: #94A3B8; font-size: 13px; font-style: italic;">[Data entry locked for {travel_date.strftime('%d %b %Y')} - Enter Admin passcode below to override]</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("🔙 GO BACK TO TODAY", key="lock_back_btn"):
        st.query_params["reset"] = "true"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# PRIORITY 3: Standard Input Form
else:
    if date_exists and is_admin_authenticated:
        st.warning(f"⚠️ Mode: Admin Override Active. Saving will overwrite the existing entry for {travel_date}.")
        
    commuters = [c for c in all_commuters if c not in st.session_state.holiday_list]
    if not commuters: 
        commuters = all_commuters

    driver = st.selectbox("Designated Driver", commuters)
    passenger_options = [c for c in commuters if c != driver]
    full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options)
    remaining_options = [p for p in passenger_options if p not in full_day]
    half_day = st.multiselect("Half-Day Passengers (₹150)", remaining_options)

    if st.button("💾 SAVE TRIP TO LEDGER"):
        if not TOKEN or not REPO:
            st.error("Setup Incomplete in Secrets panel.")
            st.stop()

        # Final Backend check
        live_check_url = f"{URL}?timestamp={datetime.datetime.now().timestamp()}"
        r_check = requests.get(live_check_url, headers=HEADERS)
        backend_date_exists = False
        
        if r_check.status_code == 200:
            c_check = base64.b64decode(r_check.json()["content"]).decode("utf-8")
            df_check = pd.read_csv(io.StringIO(c_check))
            if not df_check.empty:
                backend_date_exists = str(travel_date) in df_check["Date"].astype(str).values

        if backend_date_exists and not is_admin_authenticated:
            st.error("🛑 Overwrite Denied: This date was just logged by someone else!")
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
        if sha: 
            payload["sha"] = sha
            
        r_put = requests.put(URL, headers=HEADERS, json=payload)
        if r_put.status_code in [200, 201]:
            praise_map = {
                "Manish": "👑 Manish - Tere jaisa koi nahi!",
                "Ankit": "✈️ Ankit - Wah kya Jahaj banaya hai!",
                "Ajay": "🌶️ Ajay - Sexy mallu Zindabad!",
                "Abhishek": "🔥 Abhishek - Wah jawani Wah!",
                "Dk": "📢 Dk - Bhag Bose DK!"
            }
            custom_message = praise_map.get(driver, f"🎉 Trip successfully saved for driver {driver}!")
            
            st.session_state.just_saved = True
            st.session_state.saved_message = custom_message
            st.session_state.disable_lock = True
            st.session_state.last_processed_date = str(travel_date)
            st.rerun()
