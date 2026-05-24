import streamlit as st
import pandas as pd
import requests
import base64
import io
import random

st.set_page_config(page_title="MG Settlement Engine", page_icon="📊", layout="wide")

# Visual Engine matching your Input App theme
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
    .matrix-val { font-size: 36px !important; font-weight: 900 !important; margin-top: 10px; }
    .val-positive { color: #4ADE80 !important; text-shadow: 0 0 10px rgba(74,222,128,0.2); }
    .val-negative { color: #F87171 !important; text-shadow: 0 0 10px rgba(248,113,113,0.2); }
    .val-zero { color: #94A3B8 !important; }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="main-title">📊 MG Carpool Settlement Engine</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

# Fetch parameters directly from your newly verified vault secrets
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

# Initialize Balances Matrix
balances = {name: 0.0 for name in all_commuters}

# 1. Process Carpool Commute Logs
if not df_trips.empty:
    for _, row in df_trips.iterrows():
        driver = str(row.get("Driver", "")).strip().title()
        
        full_passengers = str(row.get("Full Day Passengers", "")).split(",")
        full_list = [p.strip().title() for p in full_passengers if p.strip() and p.strip().lower() != 'none']
        
        half_passengers = str(row.get("Half Day Passengers", "")).split(",")
        half_list = [p.strip().title() for p in half_passengers if p.strip() and p.strip().lower() != 'none']
        
        total_trip_earnings = 0.0
        
        # Deduct from passengers, track driver earnings
        for p in full_list:
            if p in balances:
                balances[p] -= 300.0
                total_trip_earnings += 300.0
                
        for p in half_list:
            if p in balances:
                balances[p] -= 150.0
                total_trip_earnings += 150.0
                
        if driver in balances:
            balances[driver] += total_trip_earnings

# 2. Process Bill Split Expenses Logs
if not df_expenses.empty:
    for _, row in df_expenses.iterrows():
        payer = str(row.get("Paid By", "")).strip().title()
        total_amt = float(row.get("Total Amount", 0.0))
        
        shared_with = str(row.get("Shared By", "")).split(",")
        shared_list = [p.strip().title() for p in shared_with if p.strip()]
        
        if total_amt > 0 and len(shared_list) > 0:
            per_head = round(total_amt / len(shared_list), 2)
            
            # Deduct individual shares
            for p in shared_list:
                if p in balances:
                    balances[p] -= per_head
            # Credit the full amount back to the payer
            if payer in balances:
                balances[payer] += total_amt

# Visual Interface Matrix Generator
st.markdown("### 🟢 Current Standing Matrix")
cols = st.columns(len(all_commuters))

for idx, name in enumerate(all_commuters):
    final_bal = round(balances[name], 2)
    with cols[idx]:
        if final_bal > 0:
            val_class = "val-positive"
            prefix = "+"
        elif final_bal < 0:
            val_class = "val-negative"
            prefix = ""
        else:
            val_class = "val-zero"
            prefix = ""
            
        st.markdown(
            f"""
            <div class="matrix-card">
                <div class="matrix-name">{name}</div>
                <div class="matrix-val {val_class}">{prefix}₹{final_bal:,}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

st.markdown("<br><hr>", unsafe_allow_html=True)

# Detailed Ledger Overviews
col_left, col_right = st.columns(2)
with col_left:
    st.markdown("#### 🚗 Historical Travel History")
    if not df_trips.empty:
        st.dataframe(df_trips.drop(columns=["Cleaned_Date_Str"], errors="ignore"), use_container_width=True)
    else:
        st.info("No recorded travel history found inside carpool_logs.csv")

with col_right:
    st.markdown("#### 🍔 Bill Split History")
    if not df_expenses.empty:
        st.dataframe(df_expenses, use_container_width=True)
    else:
        st.info("No expense entries logged inside carpool_expenses.csv")
