import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random

st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

# Visual Engine: Clean High-Contrast Glassmorphism Stacking System
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.95) 100%), 
                    url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80') !important;
        background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
    }
    .block-container {
        background: rgba(15, 23, 42, 0.8) !important; backdrop-filter: blur(12px) !important;
        padding: 25px !important; border-radius: 20px !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5) !important; margin-top: 20px !important;
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
    .neon-badge { display: inline-block; padding: 6px 14px; font-size: 11px; font-weight: 900; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .badge-driver { background-color: rgba(34, 197, 94, 0.25); color: #4ADE80; border: 1px solid #22C55E; box-shadow: 0 0 12px rgba(34,197,94,0.4); }
    .badge-full { background-color: rgba(56, 189, 248, 0.25); color: #38BDF8; border: 1px solid #0EA5E9; box-shadow: 0 0 12px rgba(56,189,248,0.4); }
    .badge-half { background-color: rgba(251, 191, 36, 0.25); color: #FBBF24; border: 1px solid #D97706; box-shadow: 0 0 12px rgba(251,191,36,0.4); }
    .badge-holiday { background-color: rgba(168, 85, 247, 0.25); color: #C084FC; border: 1px solid #9333EA; }
    .lock-banner { background-color: #0F172A; border: 2px solid #EF4444; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0px 0px 20px rgba(239, 68, 68, 0.3); }
    .future-banner { background-color: #0F172A; border: 2px solid #EAB308; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0px 0px 20px rgba(234, 179, 8, 0.3); }
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

# CORE SYNCHRONIZATION INITIALIZATION WITH CACHE OVERRIDES
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

# TAB 1: COMMUTE LOGGING
with tab_trip:
    travel_date = st.date_input("Date of Travel", today_date_ist, key="trip_date_norm")

    if st.session_state.last_processed_date != str(travel_date):
        st.session_state.disable_lock = False
        st.session_state.last_processed_date = str(travel_date)

    is_future_date = travel_date > today_date_ist
    
    # NORMALIZATION STRING MATCHING STRATEGY
    date_exists = False
    if not df_existing.empty and "Date" in df_existing.columns:
        target_str = travel_date.strftime("%Y-%m-%d").strip()
        df_existing["Cleaned_Date_Str"] = pd.to_datetime(df_existing["Date"], errors='coerce').dt.strftime("%Y-%m-%d").str.strip()
        date_exists = target_str in df_existing["Cleaned_Date_Str"].values

    if is_future_date:
        st.markdown("<div class='future-banner'><h1 style='font-size:50px;margin:0;'>🔮</h1><h2 style='font-size:32px;color:#EAB308;font-weight:900;margin:10px 0;'>Ye kam bhi Loudu ka hi hai</h2><h4 style='font-size:18px;color:#F1F5F9;font-weight:700;'>You cannot log entries for future dates.</h4></div>", unsafe_allow_html=True)

    elif st.session_state.just_saved:
        st.success(st.session_state.saved_message)
        st.session_state.just_saved = False
        time.sleep(1.5)
        st.rerun()

    # THE CHOSEN ONE: THE "LOUDU" LOCK BANNER ACTIVATION BOUNDARY
    elif date_exists and not st.session_state.is_admin and not st.session_state.disable_lock:
        st.markdown("<div class='lock-banner'><h1 style='font-size:50px;margin:0;'>🛑</h1><h2 style='font-size:32px;color:#EF4444;font-weight:900;margin:10px 0;'>Abe Loudu dubara kyun kar raha!</h2><h4 style='font-size:18px;color:#F1F5F9;font-weight:700;'>Ab mantri karega Sahi.</h4></div>", unsafe_allow_html=True)

    else:
        commuters = [c for c in all_commuters if c not in st.session_state.holiday_list]
        if not commuters: commuters = all_commuters

        st.markdown("#### ⚡ Real-Time Status Preview")
        preview_cols = st.columns(len(all_commuters))
        
        t_driver = st.session_state.get("temp_driver", commuters[0])
        t_full = st.session_state.get("temp_full", [])
        t_half = st.session_state.get("temp_half", [])

        for idx, person in enumerate(all_commuters):
            with preview_cols[idx]:
                st.markdown(f"<div style='text-align: center; font-weight: 800; margin-bottom: 4px; color: #FFFFFF;'>{person}</div>", unsafe_allow_html=True)
                if person in st.session_state.holiday_list:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-holiday">🌴 Leave</span></div>', unsafe_allow_html=True)
                elif person == t_driver:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-driver">👑 Wheel</span></div>', unsafe_allow_html=True)
                elif person in t_full:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-full">🚗 Full</span></div>', unsafe_allow_html=True)
                elif person in t_half:
                    st.markdown('<div style="text-align:center;"><span class="neon-badge badge-half">🌤️ Half</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="text-align:center; color:rgba(255,255,255,0.4); font-size:11px; margin-top:5px;">---</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        driver = st.selectbox("Designated Driver", commuters, key="driver_select_box")
        st.session_state.temp_driver = driver
        
        passenger_options = [c for c in commuters if c != driver]
        full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options, key="full_select_box")
        st.session_state.temp_full = full_day
        
        half_day = st.multiselect("Half-Day Passengers (₹150)", [p for p in passenger_options if p not in full_day], key="half_select_box")
        st.session_state.temp_half = half_day

        if st.button("💾 SAVE TRIP TO LEDGER"):
            # BACKEND FALLBACK LOCKDOWN VERIFICATION
            is_valid_submission = True
            if TOKEN and REPO:
                try:
                    r_emergency = requests.get(f"{TRIP_URL}?final_check={random.randint(1, 1000000)}", headers=HEADERS)
                    if r_emergency.status_code == 200:
                        df_emergency = pd.read_csv(io.StringIO(base64.b64decode(r_emergency.json()["content"]).decode("utf-8")))
                        if not df_emergency.empty and "Date" in df_emergency.columns:
                            t_emergency_str = travel_date.strftime("%Y-%m-%d").strip()
                            df_emergency["Emergency_Date_Str"] = pd.to_datetime(df_emergency["Date"], errors='coerce').dt.strftime("%Y-%m-%d").str.strip()
                            if t_emergency_str in df_emergency["Emergency_Date_Str"].values and not st.session_state.is_admin:
                                is_valid_submission = False
                except Exception:
                    pass

            if not is_valid_submission:
                st.error("🛑 Abe Loudu, data already exists on GitHub! Refreshing page...")
                time.sleep(2)
                st.rerun()
            else:
                full_str = ", ".join([p.strip().title() for p in full_day]) if full_day else "None"
                half_str = ", ".join([p.strip().title() for p in half_day]) if half_day else "None"
                
                new_row = pd.DataFrame([{"Date": str(travel_date), "Driver": driver.strip().title(), "Full Day Passengers": full_str, "Half Day Passengers": half_str}])
                df_final = pd.concat([df_existing[df_existing["Date"].astype(str) != str(travel_date)], new_row], ignore_index=True) if not df_existing.empty else new_row
                
                if "Cleaned_Date_Str" in df_final.columns: df_final = df_final.drop(columns=["Cleaned_Date_Str"])
                if "Emergency_Date_Str" in df_final.columns: df_final = df_final.drop(columns=["Emergency_Date_Str"])
                
                payload = {"message": f"Update trip logs for {travel_date}", "content": base64.b64encode(df_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
                
                r_sha = requests.get(f"{TRIP_URL}?getsha={random.randint(1, 1000000)}", headers=HEADERS)
                if r_sha.status_code == 200: payload["sha"] = r_sha.json()["sha"]
                
                if requests.put(TRIP_URL, headers=HEADERS, json=payload).status_code in [200, 201]:
                    try:
                        w_msg = (
                            f"🌅 *MG Carpool Hub Summary — {travel_date}*\n\n"
                            f"👑 *Driver:* {driver.strip().title()}\n"
                            f"🚗 *Full-Day Passengers:* {full_str}\n"
                            f"🌤️ *Half-Day Passengers:* {half_str}\n\n"
                            f"📊 _Ledger updated seamlessly!_ 💸"
                        )
                        g_instance = st.secrets['GREEN_INSTANCE_ID']
                        g_token = st.secrets['TOKEN_PART_1'] + st.secrets['TOKEN_PART_2']
                        w_url = f"https://api.green-api.com/waInstance{g_instance}/sendMessage/{g_token}"
                        w_payload = {"chatId": st.secrets['WHATSAPP_GROUP_ID'], "message": w_msg}
                        requests.post(w_url, json=w_payload, headers={"Content-Type": "application/json"}, timeout=5)
                    except Exception:
                        pass

                    st.toast(f"🚗 Commute log saved for {travel_date}!", icon="✅")
                    st.balloons()
                    st.session_state.just_saved = True
                    st.session_state.saved_message = f"🎉 Trip saved & WhatsApp Group Notified!"
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
                
                r_exp_sha = requests.get(f"{EXPENSE_URL}?getexpsha={random.randint(1, 1000000)}", headers=HEADERS)
                if r_exp_sha.status_code == 200: payload_exp["sha"] = r_exp_sha.json()["sha"]
                
                if requests.put(EXPENSE_URL, headers=HEADERS, json=payload_exp).status_code in [200, 201]:
                    st.toast(f"💸 Bill split recorded for {item_desc}!", icon="💰")
                    st.success("💸 Expense Saved Successfully!")
                    time.sleep(1.5)
                    st.rerun()

# MASTER ADMIN CONTROLS INTERFACE PANEL
st.markdown("---")
with st.expander("🛠️ Admin Controls (Authorized Only)"):
    if not st.session_state.is_admin:
        admin_pin = st.text_input("Enter Admin PIN", type="password", key="pin_input_field")
        if admin_pin == "9999":
            st.session_state.is_admin = True
            st.rerun()
    
    if st.session_state.is_admin:
        st.success("Admin Rights Unlocked")
        if st.button("🔙 EXIT ADMIN MODE"):
            st.session_state.is_admin = False
            st.rerun()
        
        st.markdown("#### 🌴 Skip This Person (Active Leave)")
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
            delete_date = st.selectbox("Select Travel Date to Delete:", sorted(df_existing["Date"].unique(), reverse=True))
            st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
            if st.button("🗑️ DELETE TRAVEL DATE"):
                df_final = df_existing[df_existing["Date"].astype(str) != str(delete_date)]
                
                if "Cleaned_Date_Str" in df_final.columns: df_final = df_final.drop(columns=["Cleaned_Date_Str"])
                if "Emergency_Date_Str" in df_final.columns: df_final = df_final.drop(columns=["Emergency_Date_Str"])
                
                payload = {"message": f"Admin delete trip: {delete_date}", "content": base64.b64encode(df_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
                r_del_sha = requests.get(f"{TRIP_URL}?delsha={random.randint(1, 1000000)}", headers=HEADERS)
                if r_del_sha.status_code == 200: payload["sha"] = r_del_sha.json()["sha"]
                
                if requests.put(TRIP_URL, headers=HEADERS, json=payload).status_code in [200, 201]:
                    st.error(f"🗑️ Travel record for {delete_date} wiped!")
                    time.sleep(1.5)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        if not df_exp_existing.empty:
            st.markdown("#### 🍔 Delete Manage Split Expenses")
            df_exp_existing['Display_Label'] = df_exp_existing['Date'].astype(str) + " | " + df_exp_existing['Paid By'] + " | ₹" + df_exp_existing['Total Amount'].astype(str) + " (" + df_exp_existing['Description'] + ")"
            selected_exp_label = st.selectbox("Select Bill Record to delete:", df_exp_existing['Display_Label'].unique())
            st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
            if st.button("🗑️ DELETE EXPENSE RECORD"):
                df_exp_final = df_exp_existing[df_exp_existing['Display_Label'] != selected_exp_label]
                if 'Display_Label' in df_exp_final.columns:
                    df_exp_final = df_exp_final.drop(columns=['Display_Label'])
                payload_exp = {"message": "Admin deleted expense", "content": base64.b64encode(df_exp_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
                
                r_exp_del_sha = requests.get(f"{EXPENSE_URL}?expdelsha={random.randint(1, 1000000)}", headers=HEADERS)
                if r_exp_del_sha.status_code == 200: payload_exp["sha"] = r_exp_del_sha.json()["sha"]
                
                if requests.put(EXPENSE_URL, headers=HEADERS, json=payload_exp).status_code in [200, 201]:
                    st.error("🗑️ Expense record wiped out successfully!")
                    time.sleep(1.5)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
