import streamlit as st
import pandas as pd
import requests
import base64
import io
import random

st.set_page_config(page_title="MG Balance Matrix", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.98) 100%), 
                    url('https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80') !important;
        background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
    }
    .block-container { background: transparent !important; }
    .card { background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: center; margin-bottom: 15px; }
    h1, h2, h3, p, span, label { color: white !important; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 MG Carpool Settlement Engine")

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")

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
        r1 = requests.get(f"{TRIP_URL}?cb={random.randint(1,1000000)}", headers=HEADERS)
        if r1.status_code == 200:
            df_trips = pd.read_csv(io.StringIO(base64.b64decode(r1.json()["content"]).decode("utf-8")))
        r2 = requests.get(f"{EXPENSE_URL}?cb={random.randint(1,1000000)}", headers=HEADERS)
        if r2.status_code == 200:
            df_expenses = pd.read_csv(io.StringIO(base64.b64decode(r2.json()["content"]).decode("utf-8")))
    except Exception as e:
        st.error(f"Read failure: {str(e)}")

all_users = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]
balances = {u: 0.0 for u in all_users}

# Commute Matrix Processor
if not df_trips.empty:
    for _, row in df_trips.iterrows():
        driver = str(row.get('Driver', '')).strip().title()
        if driver in balances:
            full_p = [p.strip().title() for p in str(row.get('Full Day Passengers', '')).split(',') if p.strip().title() in balances]
            half_p = [p.strip().title() for p in str(row.get('Half Day Passengers', '')).split(',') if p.strip().title() in balances]
            
            for p in full_p:
                balances[p] -= 300.0
                balances[driver] += 300.0
            for p in half_p:
                balances[p] -= 150.0
                balances[driver] += 150.0

# Bill Split Processor
if not df_expenses.empty:
    for _, row in df_expenses.iterrows():
        payer = str(row.get('Paid By', '')).strip().title()
        amt = float(row.get('Total Amount', 0.0))
        shared_by = [p.strip().title() for p in str(row.get('Shared By', '')).split(',') if p.strip().title() in balances]
        
        if payer in balances and shared_by:
            per_head = amt / len(shared_by)
            balances[payer] += amt
            for p in shared_by:
                balances[p] -= per_head

st.markdown("### 💸 Current Standing Matrix")
cols = st.columns(len(all_users))
for idx, user in enumerate(all_users):
    with cols[idx]:
        bal = round(balances[user], 2)
        color = "#4ADE80" if bal >= 0 else "#F87171"
        st.markdown(f"""
            <div class="card">
                <h3>{user}</h3>
                <h2 style='color:{color} !important;'>₹{bal}</h2>
            </div>
        """, unsafe_allow_html=True)
