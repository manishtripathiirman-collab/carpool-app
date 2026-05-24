import streamlit as st
import pandas as pd
import requests
import base64
import io
import random

st.set_page_config(page_title="MG Settlement Engine", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0F172A !important; }
    .block-container {
        background: rgba(30, 41, 59, 0.7) !important;
        padding: 30px !important; 
        border-radius: 20px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5) !important; 
        margin-top: 20px !important;
    }
    .main-title { font-family: sans-serif; font-size: 32px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 25px; }
    .matrix-card {
        background: linear-gradient(135deg, #1E293B, #0F172A) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }
    .matrix-name { font-size: 20px !important; font-weight: 800 !important; color: #94A3B8 !important; }
    .matrix-val { font-size: 34px !important; font-weight: 900 !important; margin-top: 10px; }
    .val-positive { color: #4ADE80 !important; }
    .val-negative { color: #F87171 !important; }
    .val-zero { color: #64748B !important; }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="main-title">📊 MG Carpool Settlement Engine</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "").strip()
REPO = st.secrets.get("GITHUB_REPO", "").strip()

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Cache-Control": "no-cache, no-store, must-revalidate"
}

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
    except Exception:
        pass

balances = {name: 0.0 for name in all_commuters}

# 1. Commute Loops (With Robust Quote Stripping)
if not df_trips.empty:
    for _, row in df_trips.iterrows():
        driver = str(row.get("Driver", "")).replace('"', '').replace("'", "").strip().title()
        
        full_raw = str(row.get("Full Day Passengers", "")).replace('"', '').replace("'", "")
        full_list = [p.strip().title() for p in full_raw.split(",") if p.strip() and p.strip().lower() != 'none']
        
        half_raw = str(row.get("Half Day Passengers", "")).replace('"', '').replace("'", "")
        half_list = [p.strip().title() for p in half_raw.split(",") if p.strip() and p.strip().lower() != 'none']
        
        trip_total = 0.0
        for p in full_list:
            if p in balances:
                balances[p] -= 300.0
                trip_total += 300.0
        for p in half_list:
            if p in balances:
                balances[p] -= 150.0
                trip_total += 150.0
                
        if driver in balances:
            balances[driver] += trip_total

# 2. Expense Loops (With Case-Insensitive Column Fallback)
if not df_expenses.empty:
    for _, row in df_expenses.iterrows():
        payer = str(row.get("Paid By", "")).replace('"', '').replace("'", "").strip().title()
        
        # Pull amount cleanly regardless of upper/lowercase column names
        total_amount = row.get("Total Amount", row.get("Total amount", 0.0))
        try:
            total_amount = float(total_amount)
        except:
            total_amount = 0.0
            
        consumers_raw = str(row.get("Shared By", "")).replace('"', '').replace("'", "")
        consumer_list = [p.strip().title() for p in consumers_raw.split(",") if p.strip()]
        
        if total_amount > 0 and len(consumer_list) > 0:
            per_person_cost = round(total_amount / len(consumer_list), 2)
            for p in consumer_list:
                if p in balances:
                    balances[p] -= per_person_cost
            if payer in balances:
                balances[payer] += total_amount

st.markdown("### 🟢 Current Standings Matrix")
cols = st.columns(len(all_commuters))
for idx, name in enumerate(all_commuters):
    val = round(balances[name], 2)
    with cols[idx]:
        if val > 0:
            v_class = "val-positive"; p_sign = "+"
        elif val < 0:
            v_class = "val-negative"; p_sign = ""
        else:
            v_class = "val-zero"; p_sign = ""
            
        st.markdown(f'<div class="matrix-card"><div class="matrix-name">{name}</div><div class="matrix-val {v_class}">{p_sign}₹{val:,}</div></div>', unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
col_left, col_right = st.columns(2)
with col_left:
    st.markdown("#### 🚗 Travel History Logs")
    if not df_trips.empty:
        st.dataframe(df_trips, use_container_width=True)
    else:
        st.info("No recorded travel history rows found.")
with col_right:
    st.markdown("#### 💰 Shared Expenses History Logs")
    if not df_expenses.empty:
        st.dataframe(df_expenses, use_container_width=True)
    else:
        st.info("No recorded expense rows found.")
