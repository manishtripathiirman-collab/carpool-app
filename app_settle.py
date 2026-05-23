import streamlit as st
import pandas as pd
import datetime
import requests
import base64
import io
import urllib.parse
import time

st.set_page_config(page_title="MG Payout & Analytics", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.94), rgba(15, 23, 42, 0.96)), 
                          url('https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=800&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border-radius: 16px; padding: 16px; margin-bottom: 12px; border: 1px solid rgba(99, 102, 241, 0.2); }
    .badge-payout { background-color: rgba(244, 63, 94, 0.15); color: #FB7185; padding: 6px 14px; border-radius: 10px; font-size: 18px; font-weight: 800; float: right; }
    .mobile-title { font-family: sans-serif; font-size: 26px !important; font-weight: 800; color: #FFFFFF; }
    label, p, span, h3, h4 { color: #CBD5E1 !important; }
    
    .whatsapp-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #25D366 !important;
        color: white !important;
        font-weight: 700;
        font-size: 16px;
        text-decoration: none;
        padding: 14px;
        border-radius: 12px;
        width: 100%;
        text-align: center;
        margin-top: 10px;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
    }
    .whatsapp-btn:hover { background-color: #20BA5A !important; text-decoration: none; color: white !important; }
    [data-testid="stMetricValue"] { color: #6366F1 !important; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">💰 MG Carpool Hub</p>', unsafe_allow_html=True)

commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

if not TOKEN or not REPO:
    st.info("💡 Awaiting cloud connection keys inside secrets panel.")
    st.stop()

# Base Content URLs
URL_TRIPS = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
URL_EXPENSES = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

# --- DATABASE FETCH ENGINE ---
df_trips = pd.DataFrame()
df_expenses = pd.DataFrame()

# Fetch Trips
r_trips = requests.get(f"{URL_TRIPS}?ts={time.time()}", headers=HEADERS)
if r_trips.status_code == 200:
    content_trips = base64.b64decode(r_trips.json()["content"]).decode("utf-8")
    df_trips = pd.read_csv(io.StringIO(content_trips))
    df_trips['Clean_Date'] = pd.to_datetime(df_trips['Date']).dt.date

# Fetch Expenses
r_expenses = requests.get(f"{URL_EXPENSES}?ts={time.time()}", headers=HEADERS)
if r_expenses.status_code == 200:
    content_expenses = base64.b64decode(r_expenses.json()["content"]).decode("utf-8")
    df_expenses = pd.read_csv(io.StringIO(content_expenses))
    df_expenses['Clean_Date'] = pd.to_datetime(df_expenses['Date']).dt.date

if not df_trips.empty:
    tab_settle, tab_charts = st.tabs(["💵 Settlements", "📊 Expense Dashboard"])
    
    with tab_settle:
        st.markdown("### 🗓️ Select Settlement Frame Window")
        col1, col2 = st.columns(2)
        with col1: start_date = st.date_input("From Date", min(df_trips['Clean_Date']), key="s_start")
        with col2: end_date = st.date_input("To Date", max(df_trips['Clean_Date']), key="s_end")
            
        filtered_trips = df_trips[(df_trips['Clean_Date'] >= start_date) & (df_trips['Clean_Date'] <= end_date)]
        
        with st.expander(f"📱 View Logged Travel History ({len(filtered_trips)} Days)", expanded=False):
            st.dataframe(filtered_trips.sort_values(by="Clean_Date", ascending=False), use_container_width=True, hide_index=True)
            
        # Running base account initialization matrix
        ledger_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
        
        # 1. PROCESS DAILY TRIP LOG COSTS
        for _, row in filtered_trips.iterrows():
            driver_matched = str(row['Driver']).strip().title()
            if driver_matched not in commuters: continue
            
            full_p = [p.strip().title() for p in str(row['Full Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
            half_p = [p.strip().title() for p in str(row['Half Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
            
            for p in full_p:
                if p in commuters and p != driver_matched:
                    ledger_debts[p][driver_matched] += 300.0
            for p in half_p:
                if p in commuters and p != driver_matched:
                    ledger_debts[p][driver_matched] += 150.0

        # 2. PROCESS SHARED EXPENSES LOG BILLS (IF DATA EXISTS)
        total_period_expenses = 0.0
        if not df_expenses.empty:
            filtered_expenses = df_expenses[(df_expenses['Clean_Date'] >= start_date) & (df_expenses['Clean_Date'] <= end_date)]
            
            if not filtered_expenses.empty:
                total_period_expenses = filtered_expenses['Total Amount'].sum()
                with st.expander(f"💰 View Shared Bills Logged In This Window (₹{total_period_expenses:,.2f})", expanded=False):
                    st.dataframe(filtered_expenses.sort_values(by="Clean_Date", ascending=False), use_container_width=True, hide_index=True)
                
                for _, row in filtered_expenses.iterrows():
                    payer = str(row['Paid By']).strip().title()
                    per_head = float(row['Per Head Cost'])
                    consumers = [p.strip().title() for p in str(row['Shared By']).split(',') if p.strip()]
                    
                    for p in consumers:
                        if p in commuters and p != payer:
                            ledger_debts[p][payer] += per_head

        # 3. PAIRWISE MINIMIZATION MATHEMATICS
        settlements = []
        for i in range(len(commuters)):
            for j in range(i + 1, len(commuters)):
                p1, p2 = commuters[i], commuters[j]
                p1_owes = ledger_debts[p1][p2]
                p2_owes = ledger_debts[p2][p1]
                
                if p1_owes > p2_owes:
                    net = p1_owes - p2_owes
                    if net > 0: settlements.append({"From": p1, "To": p2, "Amount": net})
                elif p2_owes > p1_owes:
                    net = p2_owes - p1_owes
                    if net > 0: settlements.append({"From": p2, "To": p1, "Amount": net})

        st.markdown("### 💰 Calculated Net Pairwise Payouts")
        if settlements:
            for s in settlements:
                st.markdown(f"""
                <div class="mobile-card">
                    <span class="badge-payout">₹{s['Amount']:.2f}</span>
                    <div style="font-weight:700; color:#F8FAFC;">👉 {s['From']}</div>
                    <div style="font-size:13px; color:#94A3B8; margin-top:4px;">Owes cash directly to <b>{s['To']}</b></div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- WHATSAPP MESSAGE ENGINE ---
            whatsapp_text = f"🚗 *Carpool Settlement Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
            whatsapp_text += f"💵 *Total Hand-Logged Expenses Shared:* ₹{total_period_expenses:,.2f}\n"
            whatsapp_text += "--------------------------------------\n"
            for s in settlements: 
                whatsapp_text += f"👉 *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.2f}*\n"
            whatsapp_text += "--------------------------------------"
            
            encoded_text = urllib.parse.quote(whatsapp_text)
            whatsapp_url = f"https://wa.me/?text={encoded_text}"
            
            st.markdown(f"""
                <a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">
                    💬 SHARE DIRECT TO WHATSAPP GROUP
                </a>
            """, unsafe_allow_html=True)
        else:
            st.success("🎉 All accounts match perfectly across this window!")

    # 🌟 DASHBOARD GRAPHICS ENGINE 🌟
    with tab_charts:
        st.markdown("### 📊 Pool Expense Analytics")
        
        total_trips = len(df_trips)
        approx_savings = total_trips * 4 * 250 
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Total Trips Run", value=f"{total_trips} Days")
        with m_col2:
            st.metric(label="Est. Group Savings", value=f"₹{approx_savings:,}")
            
        st.markdown("---")
        
        # Chart 1: Driver Frequency
        st.markdown("#### 🚘 Driver Frequency Leaderboard")
        driver_counts = df_trips['Driver'].value_counts()
        driver_chart_data = pd.DataFrame(0, index=commuters, columns=['Trips Driven'])
        for comm in commuters:
            if comm in driver_counts.index:
                driver_chart_data.loc[comm, 'Trips Driven'] = driver_counts[comm]
        st.bar_chart(driver_chart_data)
        
        # Chart 2: Cumulative Expense Matrix Contribution
        st.markdown("#### 💸 Gross Passenger Spending (Owed to Pool)")
        passenger_spending = {c: 0.0 for c in commuters}
        
        for _, row in df_trips.iterrows():
            dr = str(row['Driver']).strip().title()
            full_p = [p.strip().title() for p in str(row['Full Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
            half_p = [p.strip().title() for p in str(row['Half Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
            
            for p in full_p:
                if p in passenger_spending and p != dr: passenger_spending[p] += 300.0
            for p in half_p:
                if p in passenger_spending and p != dr: passenger_spending[p] += 150.0
                
        spending_df = pd.DataFrame.from_dict(passenger_spending,
