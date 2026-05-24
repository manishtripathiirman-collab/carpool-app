import streamlit as st
import pandas as pd
import requests
import base64
import io
import random
import datetime
import urllib.parse

st.set_page_config(page_title="MG Settlement", page_icon="📊", layout="centered")

# Visual Engine: Ultra-Lean Cyber-Dark Settlement Theme
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0F172A !important; }
    .block-container {
        background: rgba(30, 41, 59, 0.5) !important;
        padding: 15px !important; border-radius: 16px !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; margin-top: 5px !important;
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
    
    /* Eco Box */
    .eco-box {
        background: linear-gradient(135deg, #064E3B, #022C22); border: 1px solid rgba(5, 150, 105, 0.4);
        border-radius: 12px; padding: 12px; margin-top: 12px;
    }
    .eco-title { color: #34D399 !important; font-size: 12px !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Compact Link Button */
    .whatsapp-btn {
        display: block; text-align: center; width: 100%; background: #10B981;
        color: white !important; border-radius: 10px; font-weight: 800; padding: 10px; text-decoration: none !important;
        font-size: 14px; box-shadow: 0px 3px 10px rgba(16, 185, 129, 0.2); font-family: sans-serif;
    }
    .whatsapp-btn:hover { background: #059669; text-decoration: none !important; }
    
    /* Minimize widget padding */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 6px 12px !important; font-size: 13px !important; }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="main-title">💰 MG Settlement Desk</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "").strip()
REPO = st.secrets.get("GITHUB_REPO", "").strip()

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "Cache-Control": "no-cache"}
TRIP_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
EXPENSE_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

df_trips = pd.DataFrame()
df_expenses = pd.DataFrame()

if TOKEN and REPO:
    try:
        r = requests.get(f"{TRIP_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r.status_code == 200:
            df_trips = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
        r_e = requests.get(f"{EXPENSE_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r_e.status_code == 200:
            df_expenses = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))
    except Exception: pass

if not df_trips.empty:
    df_trips["Date"] = pd.to_datetime(df_trips["Date"], errors='coerce')
if not df_expenses.empty:
    df_expenses["Date"] = pd.to_datetime(df_expenses["Date"], errors='coerce')

st.markdown('<p class="section-title">📅 Settlement Week</p>', unsafe_allow_html=True)

# Dynamic Time Window Math
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

# --- MATRIX LOGIC CORE ---
driver_counts = {name: 0 for name in all_commuters}
passenger_counts = {name: 0 for name in all_commuters}
total_trips_logged = 0
balances = {name: 0.0 for name in all_commuters}

eco_saved_footprint = {
    "Manish": 130 * 0.16,     
    "Abhishek": 130 * 0.13,   
    "Dk": 130 * 0.09,         
    "Ajay": 130 * 0.09,       
    "Ankit": 130 * 0.09       
}
total_carbon_offset_kg = 0.0

if not df_trips.empty:
    total_trips_logged = len(df_trips)
    for _, row in df_trips.iterrows():
        driver = str(row.get("Driver", "")).strip().title()
        full_list = [p.strip().title() for p in str(row.get("Full Day Passengers", "")).split(",") if p.strip() and p.strip().lower() != 'none']
        half_list = [p.strip().title() for p in str(row.get("Half Day Passengers", "")).split(",") if p.strip() and p.strip().lower() != 'none']
        
        if driver in driver_counts: driver_counts[driver] += 1
            
        for p in full_list:
            if p in passenger_counts: passenger_counts[p] += 1
            if p in balances: balances[p] -= 300.0
            if driver in balances: balances[driver] += 300.0
            if p in eco_saved_footprint: total_carbon_offset_kg += eco_saved_footprint[p]
            
        for p in half_list:
            if p in passenger_counts: passenger_counts[p] += 1
            if p in balances: balances[p] -= 150.0; balances[driver] += 150.0
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
                if p in balances: balances[p] -= per_person_cost
            if payer in balances: balances[payer] += total_amount

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
    st.markdown('<p class="section-title">💎 Net Pairwise Settlements</p>', unsafe_allow_html=True)
    
    debtors = []
    creditors = []
    for person, bal in balances.items():
        if bal < -0.01: debtors.append([person, abs(bal)])
        elif bal > 0.01: creditors.append([person, bal])
            
    pairwise_txs = []
    d_idx, c_idx = 0, 0
    while d_idx < len(debtors) and c_idx < len(creditors):
        d_name, d_amt = debtors[d_idx]
        c_name, c_amt = creditors[c_idx]
        settled_amt = min(d_amt, c_amt)
        pairwise_txs.append((d_name, c_name, round(settled_amt, 2)))
        debtors[d_idx][1] -= settled_amt
        creditors[c_idx][1] -= settled_amt
        if debtors[d_idx][1] < 0.01: d_idx += 1
        if creditors[c_idx][1] < 0.01: c_idx += 1

    # Text Generator
    whatsapp_lines = ["*🚗 Carpool Settlement Summary*", "-------------------------------------"]
    if not pairwise_txs:
        st.info("Balances are fully zeroed out!")
    else:
        for deb, cred, amt in pairwise_txs:
            st.markdown(f'<div class="pairwise-card"><div><div class="payer-info">👉 {deb}</div><div class="payer-sub">Pays directly to <b>{cred}</b></div></div><div class="payout-pill">₹{amt:,.0f}</div></div>', unsafe_allow_html=True)
            whatsapp_lines.append(f"👉 *{deb}* pays *{cred}*:  *₹{amt:.0f}*")
            
    whatsapp_lines.append("-------------------------------------")
    whatsapp_lines.append("💡 _Calculated via direct netting loops._")
    whatsapp_text_raw = "\n".join(whatsapp_lines)

    st.markdown('<p class="section-title">🟢 Output Code</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="whatsapp-box">{whatsapp_text_raw.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Direct Share Link
    encoded_message = urllib.parse.quote(whatsapp_text_raw)
    whatsapp_link_html = f"""
    <a href="https://api.whatsapp.com/send?text={encoded_message}" target="_blank" class="whatsapp-btn">
        💬 SHARE DIRECT TO WHATSAPP
    </a>
    """
    st.markdown(whatsapp_link_html, unsafe_allow_html=True)

    # Lean Eco Impact Panel
    tree_days_saved = int(total_carbon_offset_kg / 0.06) 
    st.markdown(
        f"""
        <div class="eco-box">
            <div class="eco-title">🌱 Eco Impact Profile</div>
            <div class="scorecard-row" style="margin-top: 6px;">
                <div class="scorecard-box" style="background:rgba(0,0,0,0.25); border:none;">
                    <div class="scorecard-label" style="color:#A7F3D0;">Avoided Footprint</div>
                    <div
