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
    .mobile-title { font-family: sans-serif; font-size: 26px !important; font-weight: 800; color: #FFFFFF; margin-bottom: 0px; }
    label, p, span { color: #CBD5E1 !important; }
    div.stButton > button { width: 100%; background-color: #6366F1 !important; color: white !important; border-radius: 12px; font-weight: 700; padding: 12px; }
    .admin-btn > div.stButton > button { background-color: #EF4444 !important; }
    .back-btn > div.stButton > button { background-color: #475569 !important; border: 1px solid #64748B !important; margin-top: 15px; }
    .exit-admin-btn > div.stButton > button { background-color: #1E293B !important; border: 1px solid #334155 !important; margin-top: 10px; color: #94A3B8 !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(30, 41, 59, 0.7) !important; 
        border: 1px solid #334155 !important;
        border-radius: 8px 8px 0px 0px; 
        padding: 10px 20px !important;
        color: #94A3B8 !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #6366F1 !important; 
        color: white !important;
        border-color: #6366F1 !important;
    }
    .lock-banner { background-color: rgba(239, 68, 68, 0.2); border: 2px solid #EF4444; padding: 25px; border-radius: 16px; text-align: center; margin-bottom: 20px; }
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

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

TRIP_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
EXPENSE_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

df_existing = pd.DataFrame()
if TOKEN and REPO:
    r = requests.get(f"{TRIP_URL}?ts={time.time()}", headers=HEADERS)
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode("utf-8")
        df_existing = pd.read_csv(io.StringIO(content))

tab_trip, tab_expense = st.tabs(["🚗 Log Commute", "💰 Split Expenses"])

# TAB 1: DAILY RIDE LOG
with tab_trip:
    if "reset" in st.query_params:
        st.query_params.clear()
        travel_date = st.date_input("Date of Travel", datetime.date.today(), key="trip_date_reset")
    else:
        travel_date = st.date_input("Date of Travel", datetime.date.today(), key="trip_date_norm")

    if st.session_state.last_processed_date != str(travel_date):
        st.session_state.disable_lock = False
        st.session_state.last_processed_date = str(travel_date)

    today_date = datetime.date.today()
    is_future_date = travel_date > today_date

    date_exists = False
    if not df_existing.empty and not is_future_date:
        date_exists = str(travel_date) in df_existing["Date"].astype(str).values

    if is_future_date:
        st.warning("⏳ FUTURE TRIPS NOT ALLOWED")
        st.markdown('<div class="future-banner"><span style="font-size: 45px;">🔮</span><h2 style="color: #EAB308; margin-top: 10px; font-weight:800; font-family:sans-serif;">Ye kam bhi Loudu ka hi hai</h2><h4 style="color: #F8FAFC; font-weight: 700; margin-top: 5px;">You cannot log entries for future dates.</h4></div>', unsafe_allow_html=True)
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙 GO BACK TO TODAY", key="future_back_btn"):
            st.query_params["reset"] = "true"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.just_saved:
        st.success(st.session_state.saved_message)
        st.session_state.just_saved = False
        st.session_state.saved_message = ""
        time.sleep(2.5)
        st.rerun()

    elif date_exists and not st.session_state.is_admin and not st.session_state.disable_lock:
        st.error("🚨 ACCESS RESTRICTED FOR THIS DATE")
        st.markdown('<div class="lock-banner"><span style="font-size: 45px;">🛑</span><h2 style="color: #EF4444; margin-top: 10px; font-weight:900; font-family:sans-serif; letter-spacing: 0.5px;">Abe Loudu dubara kyun kar raha!</h2><h4 style="margin: 12px 0 0 0; color: #F8FAFC; font-weight: 700;">Ab mantri karega Sahi.</h4></div>', unsafe_allow_html=True)
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🔙 GO BACK TO TODAY", key="lock_back_btn"):
            st.query_params["reset"] = "true"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        commuters = [c for c in all_commuters if c not in st.session_state.holiday_list]
        if not commuters: commuters = all_commuters

        driver = st.selectbox("Designated Driver", commuters)
        passenger_options = [c for c in commuters if c != driver]
        full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options)
        remaining_options = [p for p in passenger_options if p not in full_day]
        half_day = st.multiselect("Half-Day Passengers (₹150)", remaining_options)

        if st.button("💾 SAVE TRIP TO LEDGER"):
            r_check = requests.get(f"{TRIP_URL}?ts={time.time()}", headers=HEADERS)
            backend_date_exists = False
            if r_check.status_code == 200:
                c_check = base64.b64decode(r_check.json()["content"]).decode("utf-8")
                df_check = pd.read_csv(io.StringIO(c_check))
                if not df_check.empty:
                    backend_date_exists = str(travel_date) in df_check["Date"].astype(str).values

            if backend_date_exists and not st.session_state.is_admin:
                st.error("🛑 Overwrite Denied!")
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
            r_exist = requests.get(TRIP_URL, headers=HEADERS)
            sha = r_exist.json()["sha"] if r_exist.status_code == 200 else None
            
            payload = {"message": f"Update trip logs for {travel_date}", "content": base64.b64encode(csv_buffers.encode("utf-8")).decode("utf-8")}
            if sha: payload["sha"] = sha
                
            r_put = requests.put(TRIP_URL, headers=HEADERS, json=payload)
            if r_put.status_code in [200, 201]:
                praise_map = {
                    "Manish": "👑 Manish - Tere jaisa koi nahi!",
                    "Ankit": "✈️ Ankit - Wah kya Jahaj banaya hai!",
                    "Ajay": "🌶️ Ajay - Sexy mallu Zindabad!",
                    "Abhishek": "🔥 Abhishek - Wah jawani Wah!",
                    "Dk": "📢 Dk - Bhag Bose DK!"
                }
                st.session_state.just_saved = True
                st.session_state.saved_message = praise_map.get(driver, f"🎉 Trip saved!")
                st.session_state.disable_lock = True
                st.session_state.last_processed_date = str(travel_date)
                st.rerun()

# TAB 2: BRAND NEW EXPENSE SPLITTER
with tab_expense:
    st.markdown("### 💰 Add Shared Expense")
    exp_date = st.date_input("Date of Expense", datetime.date.today(), key="exp_date_picker")
    payer = st.selectbox("Who Paid the Bill?", all_commuters, key="exp_payer")
    amount = st.number_input("Total Amount Spent (₹)", min_value=0.0, step=50.0)
    item_desc = st.text_input("What was this for?", placeholder="e.g., Highway Toll, Petrol, Snacks")
    
    st.markdown("**Who was in the car? (Cost splits equally)**")
    selected_consumers = []
    cols = st.columns(len(all_commuters))
    for idx, person in enumerate(all_commuters):
        with cols[idx]:
            is_checked = st.checkbox(person, value=(person == payer), key=f"share_{person}")
            if is_checked: selected_consumers.append(person)

    if st.button("💸 DISTRIBUTE & SAVE EXPENSE"):
        if amount <= 0 or not item_desc or len(selected_consumers) == 0:
            st.error("Fill all details properly!")
        else:
            with st.spinner("Saving expense..."):
                split_share = round(amount / len(selected_consumers), 2)
                consumers_str = ", ".join(selected_consumers)
                
                df_expenses = pd.DataFrame()
                r_exp = requests.get(f"{EXPENSE_URL}?ts={time.time()}", headers=HEADERS)
                sha_exp = None
                
                if r_exp.status_code == 200:
                    sha_exp = r_exp.json()["sha"]
                    c_exp = base64.b64decode(r_exp.json()["content"]).decode("utf-8")
                    df_expenses = pd.read_csv(io.StringIO(c_exp))
                
                new_exp_row = pd.DataFrame([{"Date": str(exp_date), "Paid By": payer, "Total Amount": amount, "Description": item_desc, "Shared By": consumers_str, "Per Head Cost": split_share}])
                
                df_exp_final = pd.concat([df_expenses, new_exp_row], ignore_index=True) if not df_expenses.empty else new_exp_row
                csv_exp_buffers = df_exp_final.to_csv(index=False)
                
                payload_exp = {"message": f"Log expense: {item_desc}", "content": base64.b64encode(csv_exp_buffers.encode("utf-8")).decode("utf-8")}
                if sha_exp: payload_exp["sha"] = sha_exp
                
                r_exp_put = requests.put(EXPENSE_URL, headers=HEADERS, json=payload_exp)
                if r_exp_put.status_code in [200, 201]:
                    st.success(f"💸 Success! ₹{amount} split among {len(selected_consumers)} people.")
                    time.sleep(2.0)
                    st.rerun()

# ADMIN CONTROLS AT BOTTOM
st.markdown("---")
if not df_existing.empty:
    with st.expander("👁️ View All Logged Days"):
        st.dataframe(df_existing.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
    with st.expander("🛠️ Admin Controls"):
        if not st.session_state.is_admin:
            admin_pin = st.text_input("Enter Admin PIN", type="password", key="pin_input_field")
            if admin_pin == "9999":
                st.session_state.is_admin = True
                st.rerun()
        if st.session_state.is_admin:
            if st.button("🔙 EXIT ADMIN MODE"):
                st.session_state.is_admin = False
                st.rerun()
