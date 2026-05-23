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
    label, p, span, h3, h4 { color: #CBD5E1 !important; }
    div.stButton > button { width: 100%; background-color: #6366F1 !important; color: white !important; border-radius: 12px; font-weight: 700; padding: 12px; }
    .admin-btn > div.stButton > button { background-color: #EF4444 !important; }
    .exit-admin-btn > div.stButton > button { background-color: #1E293B !important; border: 1px solid #334155 !important; margin-top: 10px; color: #94A3B8 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(30, 41, 59, 0.7) !important; border: 1px solid #334155 !important; border-radius: 8px 8px 0px 0px; padding: 10px 20px !important; color: #94A3B8 !important; }
    .stTabs [aria-selected="true"] { background-color: #6366F1 !important; color: white !important; border-color: #6366F1 !important; }
    .lock-banner { background-color: rgba(239, 68, 68, 0.2); border: 2px solid #EF4444; padding: 25px; border-radius: 16px; text-align: center; margin-bottom: 20px; }
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
df_exp_existing = pd.DataFrame()

if TOKEN and REPO:
    # Fetch trips
    r = requests.get(f"{TRIP_URL}?ts={time.time()}", headers=HEADERS)
    if r.status_code == 200:
        df_existing = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
    # Fetch expenses
    r_e = requests.get(f"{EXPENSE_URL}?ts={time.time()}", headers=HEADERS)
    if r_e.status_code == 200:
        df_exp_existing = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))

tab_trip, tab_expense = st.tabs(["🚗 Log Commute", "💰 Split Expenses"])

# TAB 1: COMMUTE LOGGING
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
    date_exists = str(travel_date) in df_existing["Date"].astype(str).values if not df_existing.empty else False

    if is_future_date:
        st.warning("⏳ FUTURE TRIPS NOT ALLOWED")
        st.markdown('<div class="lock-banner"><h2>🔮 Ye kam bhi Loudu ka hi hai</h2></div>', unsafe_allow_html=True)
    elif st.session_state.just_saved:
        st.success(st.session_state.saved_message)
        st.session_state.just_saved = False
        time.sleep(2.0)
        st.rerun()
    elif date_exists and not st.session_state.is_admin and not st.session_state.disable_lock:
        st.error("🚨 ACCESS RESTRICTED FOR THIS DATE")
    else:
        commuters = [c for c in all_commuters if c not in st.session_state.holiday_list]
        driver = st.selectbox("Designated Driver", commuters)
        passenger_options = [c for c in commuters if c != driver]
        full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options)
        half_day = st.multiselect("Half-Day Passengers (₹150)", [p for p in passenger_options if p not in full_day])

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
                st.session_state.saved_message = f"🎉 Trip saved for driver {driver}!"
                st.session_state.disable_lock = True
                st.rerun()

# TAB 2: EXPENSE LOGGING
with tab_expense:
    st.markdown("### 💰 Add Shared Expense")
    exp_date = st.date_input("Date of Expense", datetime.date.today(), key="exp_date_picker")
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

# MASTER ADMIN CONTROLS INTERFACE PANEL AT THE BOTTOM
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
        
        # --- CARPOOL TRIP DELETE CONTROL ---
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
        
        # --- NEW: SHARED EXPENSE DELETE CONTROL CONTROL ---
        if not df_exp_existing.empty:
            st.markdown("#### 🍔 Delete / Manage Split Expenses")
            
            # Formats a drop-down label string so admin can tell bills apart easily
            df_exp_existing['Display_Label'] = df_exp_existing['Date'].astype(str) + " | " + df_exp_existing['Paid By'] + " | ₹" + df_exp_existing['Total Amount'].astype(str) + " (" + df_exp_existing['Description'] + ")"
            
            selected_exp_label = st.selectbox("Select specific Bill Record to delete:", df_exp_existing['Display_Label'].unique())
            
            st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
            if st.button("🗑️ PERMANENTLY DELETE CHOSEN EXPENSE RECORD"):
                # Clean drop filter matching everything except the chosen visual dropdown row
                df_exp_final = df_exp_existing[df_exp_existing['Display_Label'] != selected_exp_label]
                # Drop the temporary lookup label before saving back to GitHub database csv file
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
        else:
            st.info("Expense database file ledger is completely empty.")
