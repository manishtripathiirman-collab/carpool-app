import streamlit as st
import pandas as pd
import datetime
import requests
import base64
import io
import urllib.parse
import time

st.set_page_config(page_title="MG Payout Summary", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.94), rgba(15, 23, 42, 0.96)), 
                          url('https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=800&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border-radius: 16px; padding: 18px; margin-bottom: 15px; border: 1px solid rgba(99, 102, 241, 0.2); }
    .badge-payout { background-color: rgba(34, 197, 94, 0.15); color: #4ADE80; padding: 8px 16px; border-radius: 10px; font-size: 20px; font-weight: 800; float: right; border: 1px solid rgba(34, 197, 94, 0.3); }
    .breakdown-text { font-size: 13px; color: #94A3B8; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.08); }
    .mobile-title { font-family: sans-serif; font-size: 26px !important; font-weight: 800; color: #FFFFFF; }
    label, p, span, h3, h4 { color: #CBD5E1 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(30, 41, 59, 0.7) !important; border: 1px solid #334155 !important; border-radius: 8px 8px 0px 0px; padding: 10px 20px !important; color: #94A3B8 !important; }
    .stTabs [aria-selected="true"] { background-color: #6366F1 !important; color: white !important; border-color: #6366F1 !important; }
    .whatsapp-btn { display: flex; align-items: center; justify-content: center; background-color: #25D366 !important; color: white !important; font-weight: 700; font-size: 16px; text-decoration: none; padding: 14px; border-radius: 12px; width: 100%; text-align: center; margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3); }
    
    .stat-container { background: rgba(15, 23, 42, 0.6); border-radius: 12px; padding: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px; }
    .stat-title { font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 15px; color: #F8FAFC; font-weight: 800; margin-top: 2px; }
    
    .eco-container {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 14px;
        padding: 16px;
        margin-top: 25px;
        margin-bottom: 10px;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.05);
    }
    .eco-headline { color: #10B981 !important; font-weight: 800; font-size: 15px; margin-bottom: 10px; letter-spacing: 0.3px; display: flex; align-items: center; gap: 6px; }
    .eco-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .eco-item { background: rgba(15, 23, 42, 0.4); padding: 10px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.1); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">💰 MG Settlement Desk</p>', unsafe_allow_html=True)

commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

if not TOKEN or not REPO:
    st.info("💡 Awaiting cloud connection keys inside secrets panel.")
    st.stop()

URL_TRIPS = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
URL_EXPENSES = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

@st.cache_data(ttl=15)
def fetch_carpool_data(url, headers):
    try:
        r = requests.get(f"{url}?cb={int(time.time() / 15)}", headers=headers)
        if r.status_code == 200:
            csv_text = base64.b64decode(r.json()["content"]).decode("utf-8")
            df = pd.read_csv(io.StringIO(csv_text))
            if not df.empty:
                df['Clean_Date'] = pd.to_datetime(df['Date']).dt.date
                return df
    except Exception:
        pass
    return pd.DataFrame()

df_trips = fetch_carpool_data(URL_TRIPS, HEADERS)
df_expenses = fetch_carpool_data(URL_EXPENSES, HEADERS)

def normalize_name(name_str):
    val = str(name_str).strip().upper()
    if val == "DK": return "Dk"
    return val.title()

if not df_trips.empty:
    st.markdown("### 🗓️ Select Calculation Date Window")
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("From Date", min(df_trips['Clean_Date']), key="s_start")
    with col2: end_date = st.date_input("To Date", max(df_trips['Clean_Date']), key="s_end")
        
    filtered_trips = df_trips[(df_trips['Clean_Date'] >= start_date) & (df_trips['Clean_Date'] <= end_date)]
    
    carpool_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
    other_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
    
    driver_tally = {c: 0 for c in commuters}
    passenger_tally = {c: 0 for c in commuters}
    
    co2_saved = 0.0
    total_fuel_liters_saved = 0.0

    # Process Travel Logs
    for _, row in filtered_trips.iterrows():
        driver_matched = normalize_name(row['Driver'])
        if driver_matched in commuters:
            driver_tally[driver_matched] += 1
            
            # 65 KM Garage Profiling
            if driver_matched == "Manish":
                co2_saved += 10.3  
                total_fuel_liters_saved += 5.2
            elif driver_matched == "Abhishek":
                co2_saved += 11.1  
                total_fuel_liters_saved += 5.8
            else:
                co2_saved += 12.2  
                total_fuel_liters_saved += 6.5
            
        full_p = [normalize_name(p) for p in str(row['Full Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        half_p = [normalize_name(p) for p in str(row['Half Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        
        for p in full_p:
            if p in commuters and p != driver_matched: 
                carpool_debts[p][driver_matched] += 300.0
                passenger_tally[p] += 1
        for p in half_p:
            if p in commuters and p != driver_matched: 
                carpool_debts[p][driver_matched] += 150.0
                passenger_tally[p] += 0.5

    # Process Split Expenses Logs
    total_period_expenses = 0.0
    filtered_expenses = pd.DataFrame()
    expense_keywords = []
    
    if not df_expenses.empty:
        filtered_expenses = df_expenses[(df_expenses['Clean_Date'] >= start_date) & (df_expenses['Clean_Date'] <= end_date)]
        if not filtered_expenses.empty:
            total_period_expenses = filtered_expenses['Total Amount'].sum()
            for _, row in filtered_expenses.iterrows():
                payer = normalize_name(row['Paid By'])
                per_head = float(row['Per Head Cost'])
                desc_text = str(row['Description']).lower()
                
                for word in ['lunch', 'food', 'turf', 'cricket', 'party', 'petrol', 'fuel', 'snack']:
                    if word in desc_text:
                        expense_keywords.append(word)
                        
                consumers = [normalize_name(p) for p in str(row['Shared By']).split(',') if p.strip()]
                for p in consumers:
                    if p in commuters and p != payer: other_debts[p][payer] += per_head

    # Calculate Pairs
    net_settlements = []
    for i in range(len(commuters)):
        for j in range(i + 1, len(commuters)):
            p1, p2 = commuters[i], commuters[j]
            
            cp_p1_owes, cp_p2_owes = carpool_debts[p1][p2], carpool_debts[p2][p1]
            misc_p1_owes, misc_p2_owes = other_debts[p1][p2], other_debts[p2][p1]
            
            total_p1_owes = cp_p1_owes + misc_p1_owes
            total_p2_owes = cp_p2_owes + misc_p2_owes
            
            if total_p1_owes > total_p2_owes:
                net = total_p1_owes - total_p2_owes
                if net > 0:
                    net_settlements.append({
                        "From": p1, "To": p2, "Amount": net,
                        "p1_cp_gross": cp_p1_owes, "p2_cp_gross": cp_p2_owes,
                        "p1_misc_gross": misc_p1_owes, "p2_misc_gross": misc_p2_owes
                    })
            elif total_p2_owes > total_p1_owes:
                net = total_p2_owes - total_p1_owes
                if net > 0:
                    net_settlements.append({
                        "From": p2, "To": p1, "Amount": net,
                        "p1_cp_gross": cp_p1_owes, "p2_cp_gross": cp_p2_owes,
                        "p1_misc_gross": misc_p1_owes, "p2_misc_gross": misc_p2_owes
                    })

    net_settlements = [s for s in net_settlements if round(s["Amount"], 2) > 0]

    # --- TOP ROW: SCORECARDS ---
    st.markdown("#### ⚡ Window Performance Scorecard")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        top_driver = max(driver_tally, key=driver_tally.get) if sum(driver_tally.values()) > 0 else "None"
        st.markdown(f'<div class="stat-container"><div class="stat-title">👑 King of Wheel</div><div class="stat-value">{top_driver} ({driver_tally.get(top_driver, 0)} Days)</div></div>', unsafe_allow_html=True)
    with m_col2:
        top_passenger = max(passenger_tally, key=passenger_tally.get) if sum(passenger_tally.values()) > 0 else "None"
        st.markdown(f'<div class="stat-container"><div class="stat-title">🎒 Top Passenger</div><div class="stat-value">{top_passenger} ({int(passenger_tally.get(top_passenger, 0))} Rides)</div></div>', unsafe_allow_html=True)

    tab_summary, tab_ledger = st.tabs(["💵 Payout Summary", "📋 Split Expense History"])

    with tab_summary:
        st.markdown("### 💎 Consolidated Net Pairwise Settlements")
        if net_settlements:
            for s in net_settlements:
                f_name, t_name = s["From"], s["To"]
                lines = []
                
                if s["p1_cp_gross"] > s["p2_cp_gross"]:
                    lines.append(f"• 🚗 **Carpool Dues:** {f_name} owes {t_name} **₹{s['p1_cp_gross'] - s['p2_cp_gross']:.0f}**")
                elif s["p2_cp_gross"] > s["p1_cp_gross"]:
                    lines.append(f"• 🚗 **Carpool Dues:** {t_name} owes {f_name} **₹{s['p2_cp_gross'] - s['p1_cp_gross']:.0f}**")
                
                if s["p1_misc_gross"] > s["p2_misc_gross"]:
                    lines.append(f"• 🍔 **Other Spend:** {f_name} owes {t_name} **₹{s['p1_misc_gross'] - s
