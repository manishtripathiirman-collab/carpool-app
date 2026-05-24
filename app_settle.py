import streamlit as st
import pandas as pd
import requests
import base64
import io
import random
import datetime

st.set_page_config(page_title="MG Settlement Desk", page_icon="📊", layout="centered")

# Visual Engine: Mobile-First Cyber-Dark Settlement Desk Theme
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0F172A !important; }
    .block-container {
        background: rgba(30, 41, 59, 0.5) !important;
        padding: 20px !important; border-radius: 24px !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; margin-top: 10px !important;
    }
    .main-title { font-size: 26px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 5px; }
    .section-title { font-size: 18px !important; font-weight: 800; color: #FFFFFF !important; margin-top: 20px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    
    /* Card Styles */
    .scorecard-box {
        background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px; padding: 14px; margin-bottom: 10px;
    }
    .scorecard-label { font-size: 11px; font-weight: 800; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }
    .scorecard-val { font-size: 16px; font-weight: 800; color: #F1F5F9; margin-top: 2px; }
    
    .pairwise-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px;
        padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;
    }
    .payer-info { font-size: 16px; font-weight: 800; color: #F1F5F9; }
    .payer-sub { font-size: 12px; font-weight: 600; color: #94A3B8; margin-top: 2px; }
    .payout-pill { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid #10B981; padding: 8px 16px; border-radius: 12px; font-size: 18px; font-weight: 900; }
    
    /* WhatsApp Box */
    .whatsapp-box { background: #151F32; border-radius: 14px; padding: 14px; border-left: 4px solid #10B981; font-family: monospace; font-size: 12px; color: #E2E8F0; }
    
    /* Eco Box */
    .eco-box {
        background: linear-gradient(135deg, #064E3B, #022C22); border: 1px solid #059669;
        border-radius: 16px; padding: 16px; margin-top: 20px;
    }
    .eco-title { color: #34D399 !important; font-size: 14px !important; font-weight: 800 !important; }
    .eco-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }
    
    /* Buttons */
    div.stButton > button { width: 100%; background: #10B981 !important; color: white !important; border-radius: 12px; font-weight: 800; padding: 12px; border: none !important; box-shadow: 0px 4px 12px rgba(16, 185, 129, 0.3); }
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

# Clean Data Structures Instantly
if not df_trips.empty:
    df_trips["Date"] = pd.to_datetime(df_trips["Date"], errors='coerce')
if not df_expenses.empty:
    df_expenses["Date"] = pd.to_datetime(df_expenses["Date"], errors='coerce')

# --- DYNAMIC BILLING WINDOW ENGINE ---
st.markdown('<p class="section-title">📅 Select Settlement Week</p>', unsafe_allow_html=True)

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

# --- SCORECARD & ECO ENGINE ---
driver_counts = {name: 0 for name in all_commuters}
passenger_counts = {name: 0 for name in all_commuters}
total_trips_logged = 0
balances = {name: 0.0 for name in all_commuters}

eco_saved_footprint = {
    "Manish": 130 * 0.16,     # Stage 4 Petrol
    "Abhishek": 130 * 0.13,   # Stage 6 Diesel
    "Dk": 130 * 0.09,         # CNG
    "Ajay": 130 * 0.09,       # CNG
    "Ankit": 130 * 0.09       # CNG
}
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

# Display Performance Scorecards
st.markdown('<p class="section-title">⚡ Weekly Performance Scorecard</p>', unsafe_allow_html=True)
top_driver = max(driver_counts, key=driver_counts.get) if total_trips_logged > 0 else "None"
top_passenger = max(passenger_counts, key=passenger_counts.get) if total_trips_logged > 0 else "None"

st.markdown(
    f"""
    <div class="scorecard-box">
        <div class="scorecard-label">👑 Weekly King of Wheel (Top Driver)</div>
        <div class="scorecard-val">{top_driver} ({driver_counts.get(top_driver, 0)} Days)</div>
    </div>
    <div class="scorecard-box">
        <div class="scorecard-label">🎒 Weekly Top Passenger</div>
        <div class="scorecard-val">{top_passenger} ({passenger_counts.get(top_passenger, 0)} Rides)</div>
    </div>
    """,
    unsafe_allow_html=True
)

tab_payout, tab_raw = st.tabs(["💵 Payout Summary", "📋 Split Expense History"])

with tab_payout:
    st.markdown('<p class="section-title">💎 Consolidated Net Pairwise Settlements</p>', unsafe_allow_html=True)
    
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

    # WhatsApp Text Builder
    whatsapp_lines = ["*🚗 Carpool Settlement Summary*", "-------------------------------------"]
    if not pairwise_txs:
        st.info("Perfect equilibrium achieved! Matrix balances are zero.")
    else:
        for deb, cred, amt in pairwise_txs:
            st.markdown(f'<div class="pairwise-card"><div><div class="payer-info">👉 {deb}</div><div class="payer-sub">Owes net single payout directly to <b>{cred}</b></div></div><div class="payout-pill">₹{amt:,.0f}</div></div>', unsafe_allow_html=True)
            whatsapp_lines.append(f"👉 *{deb}* pays *{cred}*:  *₹{amt:.0f}*")
            
    whatsapp_lines.append("-------------------------------------")
    whatsapp_lines.append("💡 _Calculated strictly via direct peer netting loops._")
    whatsapp_text_raw = "\n".join(whatsapp_lines)

    st.markdown('<p class="section-title">🟢 Summary Output Container</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="whatsapp-box">{whatsapp_text_raw.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # AIRTIGHT FIX: HTML-based clipboard interaction to safely handle text copies on mobile/web viewports
    escaped_text = whatsapp_text_raw.replace("'", "\\'").replace("\n", "\\n")
    copy_button_html = f"""
    <button onclick="navigator.clipboard.writeText('{escaped_text}'); alert('📋 Summary text copied to clipboard successfully! Open WhatsApp and paste.');" 
    style="width:100%; background:linear-gradient(90deg, #10B981, #059669); color:white; border-radius:12px; font-weight:800; padding:14px; border:none; cursor:pointer; font-size:16px; box-shadow:0px 4px 12px rgba(16, 185, 129, 0.3);">
        📋 COPY FOR WHATSAPP GROUP CHAT
    </button>
    """
    st.components.v1.html(copy_button_html, height=60)

    # Eco Impact Panel
    tree_days_saved = int(total_carbon_offset_kg / 0.06) 
    st.markdown(
        f"""
        <div class="eco-box">
            <div class="eco-title">🌱 MG Garage Eco Impact Flex (Custom Fuel Matrix)</div>
            <div class="eco-grid">
                <div class="scorecard-box" style="margin:0; background:rgba(0,0,0,0.2);">
                    <div class="scorecard-label" style="color:#A7F3D0;">🚗 Avoided Footprint</div>
                    <div class="scorecard-val" style="color:#34D399; font-size:20px;">{total_carbon_offset_kg:.1f} kg CO₂</div>
                </div>
                <div class="scorecard-box" style="margin:0; background:rgba(0,0,0,0.2);">
                    <div class="scorecard-label" style="color:#A7F3D0;">🌲 Equivalency Scale</div>
                    <div class="scorecard-val" style="color:#34D399; font-size:20px;">{tree_days_saved} Tree-Days</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab_raw:
    st.markdown("#### 🛒 Current Ledger Subsets")
    if not df_expenses.empty:
        st.dataframe(df_expenses.drop(columns=["Date"], errors="ignore"), use_container_width=True)
    else:
        st.info("No shared bills captured inside this timeline window.")
