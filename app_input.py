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
    .exit-admin-btn > div.stButton > button { background-color: #1E293B !important; border: 1px solid #334155 !important; margin-top: 10px; color: #94A3B8 !important; }
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

# India Standard Time Alignment Engine
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
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙 GO BACK TO TODAY", key="lock_back_btn"):
            st.query_params["reset"] = "true"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # FIXED: Safety fall-through ensures commuters baseline list is never empty, even on a weekend
        commuters = [c for c in all_commuters if c not in st.session_state.holiday_list]
        if not commuters: 
            commuters = all_commuters

        st.markdown("#### ⚡ Real-Time Status Preview")
        preview_cols = st.columns(len(all_commuters))
        
        t_driver = st.session_state.get("temp_driver", commuters[0])
        t_full = st.session_state.get("temp_full", [])
        t_half = st.session_state.get("temp_half", [])

        for idx, person in enumerate(all_commuters):
            with preview_cols[idx]:
                st.markdown(f"<div style='text-align: center; font-weight: 700; margin-bottom: 2px;'>{person}</div>", unsafe_allow_html=True)
                if person in st.session_state.holiday_list:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-holiday">🌴 Leave</span></div>', unsafe_allow_html=True)
                elif person == t_driver:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-driver">👑 Wheel</span></div>', unsafe_allow_html=True)
                elif person in t_full:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-full">🚗 Full</span></div>', unsafe_allow_html=True)
                elif person in t_half:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-half">🌤️ Half</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="text-align:center; color:#475569; font-size:11px; margin-top:5px;">---</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        driver = st.selectbox("Designated Driver", commuters, key="driver_select_box")
        st.session_state.temp_driver = driver
        
        passenger_options = [c for c in commuters if c != driver]
        full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options, key="full_select_box")
        st.session_state.temp_full = full_day
        
        half_day = st.multiselect("Half-Day Passengers (₹150)", [p for p in passenger_options if p not in full_day], key="half_select_box")
        st.session_state.temp_half = half_day

        if st.button("💾 SAVE TRIP TO LEDGER"):
            full_day_str = ", ".join([p.strip().title() for p in full_day]) if full_day else "None"
            half_day_str = ", ".join([p.strip().title() for p in half_day]) if half_day else "None"
            new_row = pd.DataFrame([{"Date": str(travel_date), "Driver": driver.strip().title(), "Full Day Passengers": full_day_str, "Half Day Passengers": half_day_str}])
            df_final = pd.concat([df_existing[df_existing["Date"].astype(str) != str(travel_date)], new_row], ignore_index=True) if not df_existing.empty else new_row
            payload = {"message": f"Update trip logs for {travel_date}", "content": base64.b64encode(df_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
            r_exist = requests.get(TRIP_URL, headers=HEADERS)
            if r_exist.status_code == 200: payload["sha"] = r_exist.json()["sha"]
            if requests.put(TRIP_URL, headers=HEADERS, json=payload).status_code in [200, 201]:
                st.session_state.just_saved = True
                st.session_state.saved_message = f"🎉 Trip saved successfully!"
                st.session_state.disable_lock = True
                st.rerun()

# TAB 2: EXPENSE LOGGING
with tab_expense:
    st.markdown("### 💰 Add Shared Expense")
    exp_date = st.date_input("Date of Expense", today_date_ist, key="exp_date_picker")
    payer = st.selectbox("Who Paid the Bill?", all_commuters, key="exp_payer")
    amount = st.number_input("Total Amount Spent (₹)", min_value=0.0, value=0.0, step=50.0)
    item_desc = st.text_input("What was this for?", placeholder="e.g., Office Lunch, Turf booking, Snacks")
    
    selected_consumers = []
    cols = st.columns(len(all_commuters))
    for idx, person in enumerate(all_commuters):
        with cols[idx]:
            if st.checkbox(person, value=(person == payer), key=f"share_{person}"):
                selected_consumers.append(person.strip().title())

    if st.button("💸 DISTRIBUTE & SAVE EXPENSE"):
        if amount <= 0.0 or not item_desc.strip() or len(selected_consumers) == 0:
            st.error("🛑 Fill all details properly!")
        else:
            with st.spinner("Saving expense..."):
                split_share = round(amount / len(selected_consumers), 2)
                new_exp_row = pd.DataFrame([{"Date": str(exp_date), "Paid By": payer.strip().title(), "Total Amount": amount, "Description": item_desc.strip(), "Shared By": ", ".join(selected_consumers), "Per Head Cost": split_share}])
                df_exp_final = pd.concat([df_exp_existing, new_exp_row], ignore_index=True) if not df_exp_existing.empty else new_exp_row
                payload_exp = {"message": f"Log expense: {item_desc}", "content": base64.b64encode(df_exp_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
                r_exp = requests.get(f"{EXPENSE_URL}?ts={time.time()}", headers=HEADERS)
                if r_exp.status_code == 200: payload_exp["sha"] = r_exp.json()["sha"]
                if requests.put(EXPENSE_URL, headers=HEADERS, json=payload_exp).status_code in [200, 201]:
                    st.success("💸 Expense Saved Successfully!")
                    time.sleep(1.5)
                    st.rerun()

# MASTER ADMIN CONTROLS INTERFACE PANEL
st.markdown("---")
with st.expander("🛠️ Admin Controls (Authorized Only)"):
    if not st.session_state.is_admin:
        admin_pin = st.text_input("Enter Admin PIN to Modify/Delete Records", type="password", key="pin_input_field")
        if admin_pin == "9999":
            st.session_state.is_admin = True
            st.rerun()
    
    if st.session_state.is_admin:
        st.success("Access Granted: Admin Rights Unlocked")
        st.markdown('<div class="exit-admin-btn">', unsafe_allow_html=True)
        if st.button("🔙 EXIT ADMIN MODE"):
            st.session_state.is_admin = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("#### 🌴 Skip This Person (Active Holiday Matrix)")
        selected_holidays = []
        h_cols = st.columns(len(all_commuters))
        for idx, person in enumerate(all_commuters):
            with h_cols[idx]:
                if st.checkbox(person, value=(person in st.session_state.holiday_list), key=f"holiday_{person}"):
                    selected_holidays.append(person)
        if sorted(selected_holidays) != sorted(st.session_state.holiday_list):
            st.session_state.holiday_list = selected_holidays
            st.rerun()
            
        st.markdown("---")
        if not df_existing.empty:
            st.markdown("#### 🚗 Delete Travel Records")
            delete_date = st.selectbox("Select Travel Date to Delete completely:", sorted(df_existing["Date"].unique(), reverse=True))
            st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
            if st.button("🗑️ PERMANENTLY DELETE CHOSEN TRAVEL DATE"):
                df_final = df_existing[df_existing["Date"].astype(str) != str(delete_date)]
                payload = {"message": f"Admin delete trip: {delete_date}", "content": base64.b64encode(df_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
                r_exist = requests.get(TRIP_URL, headers=HEADERS)
                if r_exist.status_code == 200: payload["sha"] = r_exist.json()["sha"]
                if requests.put(TRIP_URL, headers=HEADERS, json=payload).status_code in [200, 201]:
                    st.error(f"🗑️ Travel record for {delete_date} wiped successfully!")
                    time.sleep(1.5)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        if not df_exp_existing.empty:
            st.markdown("#### 🍔 Delete / Manage Split Expenses")
            df_exp_existing['Display_Label'] = df_exp_existing['Date'].astype(str) + " | " + df_exp_existing['Paid By'] + " | ₹" + df_exp_existing['Total Amount'].astype(str) + " (" + df_exp_existing['Description'] + ")"
            selected_exp_label = st.selectbox("Select specific Bill Record to delete:", df_exp_existing['Display_Label'].unique())
            st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
            if st.button("🗑️ PERMANENTLY DELETE CHOSEN EXPENSE RECORD"):
                df_exp_final = df_exp_existing[df_exp_existing['Display_Label'] != selected_exp_label]
                if 'Display_Label' in df_exp_final.columns:
                    df_exp_final = df_exp_final.drop(columns=['Display_Label'])
                payload_exp = {"message": "Admin deleted an expense entry", "content": base64.b64encode(df_exp_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
                r_exp = requests.get(f"{EXPENSE_URL}?ts={time.time()}", headers=HEADERS)
                if r_exp.status_code == 200: payload_exp["sha"] = r_exp.json()["sha"]
                if requests.put(EXPENSE_URL, headers=HEADERS, json=payload_exp).status_code in [200, 201]:
                    st.error("🗑️ Expense record wiped out successfully!")
                    time.sleep(1.5)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
