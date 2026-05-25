import streamlit as st
import pandas as pd
import requests
import base64
import io
import random
import datetime
import urllib.parse

st.set_page_config(page_title="MG Settlement", page_icon="📊", layout="centered")

# Visual Engine: Ultra-Lean Cyber-Dark Theme with Sustainability Canvas Styling
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
    
    /* Sustainability Eco-Impact Profile Box */
    .eco-flex-card {
        background: linear-gradient(135deg, #064E3B, #022C22);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 14px;
        padding: 16px;
        margin-top: 14px;
        margin-bottom: 10px;
        box-shadow: 0px 8px 25px rgba(4, 120, 87, 0.15);
    }
    .eco-flex-title {
        font-family: sans-serif;
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #34D399 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .eco-metric-num {
        font-size: 28px !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        line-height: 1;
    }
    .eco-metric-unit {
        font-size: 14px !important;
        color: #A7F3D0 !important;
        font-weight: 600;
    }
    .eco-sub-text {
        font-size: 12px !important;
        color: #D1FAE5 !important;
        font-weight: 500;
        margin-top: 4px;
        opacity: 0.85;
    }

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
            df_exp_existing = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))
    except Exception: pass

df_trips = df_trips_raw.copy()
df_expenses = df_exp_existing.copy() if 'df_exp_existing' in locals() else df_expenses_raw.copy()

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

# Initialize pairwise direct matrix
pairwise_matrix = {payer: {payee: 0.0 for payee in all_commuters} for payer in all_commuters}

driver_counts = {name: 0 for name in all_commuters}
passenger_counts = {name: 0 for name in all_commuters}
total_trips_logged = 0

# Fixed Sustainability Formula Factor Matrix (130 KM Round-Trip baseline metric)
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
                pairwise_matrix[p][driver] += 300.0
            # 130 KM * 0.15 kg CO2 per km saved per passenger asset signature
            total_carbon_offset_kg += (130.0 * 0.15)
            
        for p in half_list:
            if p in passenger_counts: passenger_counts[p] += 1
            if p in all_commuters and driver in all_commuters and p != driver:
                pairwise_matrix[p][driver] += 150.0
            total_carbon_offset_kg += (130.0 * 0.15 * 0.5)

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
                    pairwise_matrix[p][payer] += per_person_cost

# Mutual Pairwise Netting Engine
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
                if net_debt > 0.01: final_settlements.append((p1, p2, net_debt))
            elif p2_owes_p1 > p1_owes_p2:
                net_debt = round(p2_owes_p1 - p1_owes_p2, 2)
                if net_debt > 0.01: final_settlements.append((p2, p1, net_
