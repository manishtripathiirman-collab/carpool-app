import streamlit as st
import pandas as pd
import requests
import base64
import io
import random
import datetime
import urllib.parse

st.set_page_config(page_title="MG Settlement", page_icon="📊", layout="centered")

# Visual Engine: Ultra-Lean Cyber-Dark Theme with Universal Mobile Scrolling Viewports
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { 
        background-color: #0F172A !important; 
        overflow-y: auto !important; 
    }
    .block-container {
        background: rgba(30, 41, 59, 0.5) !important;
        padding: 15px !important; 
        border-radius: 16px !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; 
        margin-top: 35px !important;
        margin-bottom: 30px !important;
    }
    .main-title { font-size: 22px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 2px; text-align: center; }
    .section-title { font-size: 15px !important; font-weight: 800; color: #94A3B8 !important; margin-top: 12px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Compact Scorecards */
    .scorecard-row { display: flex; gap: 8px; margin-bottom: 5px; }
    .scorecard-box {
        flex: 1; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px; padding: 10px; text-align: center;
    }
    .scorecard-label { font-size: 10px; font-weight: 800; color: #64748B; text-transform: uppercase; }
    .scorecard-val { font-size: 14px; font-weight: 800; color: #F1F5F9; margin-top: 2px; }
    
    /* Lean Pairwise Cards */
    .pairwise-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px;
        padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
    }
    .payer-info { font-size: 14px; font-weight: 800; color: #F1F5F9; }
    .payer-sub { font-size: 11px; font-weight: 600; color: #64748B; }
    .payout-pill { background: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid #10B981; padding: 4px 10px; border-radius: 8px; font-size: 15px; font-weight: 900; }
    
    /* WhatsApp Box */
    .whatsapp-box { background: #151F32; border-radius: 10px; padding: 10px; border-left: 3px solid #10B981; font-family: monospace; font-size: 11px; color: #E2E8F0; }
    
    /* Compact Link Button */
    .whatsapp-btn {
        display: block; text-align: center; width: 100%; background: #10B981;
        color: white !important; border-radius: 10px; font-weight: 800; padding: 10px; text-decoration: none !important;
        font-size: 14px; box-shadow: 0px 3px 10px rgba(16, 185, 129, 0.2); font-family: sans-serif;
    }
    .whatsapp-btn:hover { background: #059669; text-decoration: none !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 6px 12px !important; font-size: 13px !important; }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="main-title">💰 MG Settlement Desk - <span style="font-size: 10px; font-weight: 400; color: #64748B; text-transform: lowercase; vertical-align: middle;">mantri</span></p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "").strip()
REPO = st.secrets.get("GITHUB_REPO", "").strip()

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "Cache-Control": "no-cache"}
TRIP_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
EXPENSE_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

df_trips_raw = pd.DataFrame()
df_expenses_raw = pd.DataFrame()

if TOKEN and REPO:
    try:
        r = requests.get(f"{TRIP_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r.status_code == 200:
            df_trips_raw = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
        r_e = requests.get(f"{EXPENSE_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r_e.status_code == 200:
            df_expenses_raw = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))
    except Exception: pass

df_trips = df_trips_raw.copy()
df_expenses = df_expenses_raw.copy()

if not df_trips.empty:
    df_trips["Date"] = pd.to_datetime(df_trips["Date"], errors='coerce')
if not df_expenses.empty:
    df_expenses["Date"] = pd.to_datetime(df_expenses["Date"], errors='coerce')

st.markdown('<p class="section-title">📅 Settlement Week</p>', unsafe_allow_html=True)

utc_now = datetime.datetime.utcnow()
ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
today = ist_now.date()

days_since_monday = today.weekday()
current_monday = today - datetime.timedelta(days=days_since_monday)
current_friday = current_monday + datetime.timedelta(days=4)

current_week_str = f"Current Week ({current_monday.strftime('%d %b')} - {current_friday.strftime('%d %b %Y')})"
past_week_str = "Week 21 (18 May - 22 May 2026)"

week_options = [current_week_str, past_week_str, "All Time Logs Cumulative"]
selected_window = st.selectbox("Choose Billing Week Window:", week_options, label_visibility="collapsed")

if selected_window == current_week_str:
    start_w = pd.to_datetime(current_monday)
    end_w = pd.to_datetime(current_friday) + datetime.timedelta(days=2)
    if not df_trips.empty:
        df_trips = df_trips[(df_trips["Date"] >= start_w) & (df_trips["Date"] <= end_w)]
    if not df_expenses.empty:
        df_expenses = df_expenses[(df_expenses["Date"] >= start_w) & (df_expenses["Date"] <= end_w)]
elif selected_window == past_week_str:
    start_w = pd.to_datetime("2026-05-18")
    end_w = pd.to_datetime("2026-05-24")
    if not df_trips.empty:
        df_trips = df_trips[(df_trips["Date"] >= start_w) & (df_trips["Date"] <= end_w)]
    if not df_expenses.empty:
        df_expenses = df_expenses[(df_expenses["Date"] >= start_w) & (df_expenses["Date"] <= end_w)]

# --- FIXED LOGIC: DIRECT PERSON-TO-PERSON DEBT MATRIX ---
# Initialize matrix for tracking person A owes person B
pairwise_matrix = {payer: {payee: 0.0 for payee in all_commuters} for payer in all_commuters}

driver_counts = {name: 0 for name in all_commuters}
passenger_counts = {name: 0 for name in all_commuters}
total_trips_logged = 0

eco_saved_footprint = {"Manish": 130*0.16, "Abhishek": 130*0.13, "Dk": 130*0.09, "Ajay": 130*0.09, "Ankit": 130*0.09}
total_carbon_offset_kg = 0.0

if not df_trips.empty:
    total_trips_logged = len(df_trips)
    for _, row in df_trips.iterrows():
        driver = str(row.get("Driver", "")).strip().title()
        full_list = [p.strip().title() for p in str(row.get("Full Day Passengers", "")).split(",") if p.strip() and p.strip().lower() != 'none']
        half_list = [p.strip().title() for p in str(row.get("Half Day Passengers", "")).split(",") if p.strip() and p.strip().lower() != 'none']
        
        if driver in driver_counts: 
            driver_counts[driver] += 1
            
        for p in full_list:
            if p in passenger_counts: passenger_counts[p] += 1
            if p in all_commuters and driver in all_commuters and p != driver:
                pairwise_matrix[p][driver] += 300.0  # Passenger pays Driver ₹300 directly
            if p in eco_saved_footprint: total_carbon_offset_kg += eco_saved_footprint[p]
            
        for p in half_list:
            if p in passenger_counts: passenger_counts[p] += 1
            if p in all_commuters and driver in all_commuters and p != driver:
                pairwise_matrix[p][driver] += 150.0  # Half-day Passenger pays Driver ₹150 directly
            if p in eco_saved_footprint: total_carbon_offset_kg += (eco_saved_footprint[p] * 0.5)

if not df_expenses.empty:
    for _, row in df_expenses.iterrows():
        payer = str(row.get("Paid By", "")).strip().title()
        try: total_amount = float(row.get("Total Amount", row.get("Total amount", 0.0)))
        except: total_amount = 0.0
        consumer_list = [p.strip().title() for p in str(row.get("Shared By", "")).split(",") if p.strip()]
        
        if total_amount > 0 and len(consumer_list) > 0:
            per_person_cost = round(total_amount / len(consumer_list), 2)
            for p in consumer_list:
                if p in all_commuters and payer in all_commuters and p != payer:
                    pairwise_matrix[p][payer] += per_person_cost  # Consumer owes Payer their split share

# Mutual Netting Loop between exact pairings (If A owes B ₹300 and B owes A ₹300, it becomes ₹0)
final_settlements = []
processed_pairs = set()

for p1 in all_commuters:
    for p2 in all_commuters:
        if p1 != p2 and (p1, p2) not in processed_pairs and (p2, p1) not in processed_pairs:
            processed_pairs.add((p1, p2))
            
            p1_owes_p2 = pairwise_matrix[p1][p2]
            p2_owes_p1 = pairwise_matrix[p2][p1]
            
            if p1_owes_p2 > p2_owes_p1:
                net_debt = round(p1_owes_p2 - p2_owes_p1, 2)
                if net_debt > 0.01:
                    final_settlements.append((p1, p2, net_debt))
            elif p2_owes_p1 > p1_owes_p2:
                net_debt = round(p2_owes_p1 - p1_owes_p2, 2)
                if net_debt > 0.01:
                    final_settlements.append((p2, p1, net_debt))

# Performance Scorecards Row
st.markdown('<p class="section-title">⚡ Weekly Stats</p>', unsafe_allow_html=True)
top_driver = max(driver_counts, key=driver_counts.get) if total_trips_logged > 0 else "None"
top_passenger = max(passenger_counts, key=passenger_counts.get) if total_trips_logged > 0 else "None"

st.markdown(
    f"""
    <div class="scorecard-row">
        <div class="scorecard-box">
            <div class="scorecard-label">👑 King of Wheel</div>
            <div class="scorecard-val">{top_driver} ({driver_counts.get(top_driver, 0)} Days)</div>
        </div>
        <div class="scorecard-box">
            <div class="scorecard-label">🎒 Top Passenger</div>
            <div class="scorecard-val">{top_passenger} ({passenger_counts.get(top_passenger, 0)} Rides)</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

tab_payout, tab_raw = st.tabs(["💵 Payouts", "📋 History"])

with tab_payout:
    st.markdown('<p class="section-title">💎 Direct Pairwise Settlements</p>', unsafe_allow_html=True)
    
    whatsapp_lines = ["*🚗 Carpool Settlement Summary*", "-------------------------------------"]
    if not final_settlements:
        st.info("Balances are fully zeroed out!")
    else:
        # Sort settlements so largest payments show first
        final_settlements.sort(key=lambda x: x[2], reverse=True)
        for deb, cred, amt in final_settlements:
            st.markdown(f'<div class="pairwise-card"><div><div class="payer-info">👉 {deb}</div><div class="payer-sub">Pays directly to <b>{cred}</b></div></div><div class="payout-pill">₹{amt:,.0f}</div></div>', unsafe_allow_html=True)
            whatsapp_lines.append(f"👉 *{deb}* pays *{cred}*:  *₹{amt:.0f}*")
            
    whatsapp_lines.append("-------------------------------------")
    whatsapp_lines.append("💡 _Calculated via strict per-ride passenger-driver isolation._")
    whatsapp_text_raw = "\n".join(whatsapp_lines)

    st.markdown('<p class="section-title">🟢 Output Code</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="whatsapp-box">{whatsapp_text_raw.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    encoded_message = urllib.parse.quote(whatsapp_text_raw)
    whatsapp_link_html = f"""
    <a href="https://api.whatsapp.com/send?text={encoded_message}" target="_blank" class="whatsapp-btn">
        💬 SHARE DIRECT TO WHATSAPP
    </a>
    """
    st.markdown(whatsapp_link_html, unsafe_allow_html=True)

    st.markdown('<p class="section-title">🌱 Eco Impact Profile</p>', unsafe_allow_html=True)
    tree_days_saved = int(total_carbon_offset_kg / 0.06)
    eco_cols = st.columns(2)
    with eco_cols[0]:
        st.metric("Avoided Footprint", f"{total_carbon_offset_kg:.1f} kg CO₂")
    with eco_cols[1]:
        st.metric("Equivalency Scale", f"{tree_days_saved} Tree-Days")

with tab_raw:
    with st.expander("🚗 View Daily Trip Logs"):
        if not df_trips.empty:
            df_trips_display = df_trips.copy()
            df_trips_display["Date"] = df_trips_display["Date"].dt.strftime('%Y-%m-%d')
            df_trips_display = df_trips_display.sort_values(by="Date", ascending=False)
            st.dataframe(df_trips_display, use_container_width=True, hide_index=True)
        else:
            st.info("No active ride history logged inside this window timeline.")

    with st.expander("💰 View Shared Expense Bills"):
        if not df_expenses.empty:
            df_expenses_display = df_expenses.copy()
            df_expenses_display["Date"] = df_expenses_display["Date"].dt.strftime('%Y-%m-%d')
            df_expenses_display = df_expenses_display.sort_values(by="Date", ascending=False)
            st.dataframe(df_expenses_display, use_container_width=True, hide_index=True)
        else:
            st.info("No active shared bills captured inside this timeline window.")
