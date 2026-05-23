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
    .badge-carpool { background-color: rgba(99, 102, 241, 0.15); color: #818CF8; padding: 6px 14px; border-radius: 10px; font-size: 18px; font-weight: 800; float: right; }
    .badge-expense { background-color: rgba(234, 179, 8, 0.15); color: #FBBF24; padding: 6px 14px; border-radius: 10px; font-size: 18px; font-weight: 800; float: right; }
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
        margin-top: 15px;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
    }
    .whatsapp-btn:hover { background-color: #20BA5A !important; text-decoration: none; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">💰 MG Carpool & Expense Hub</p>', unsafe_allow_html=True)

commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

if not TOKEN or not REPO:
    st.info("💡 Awaiting cloud connection keys inside secrets panel.")
    st.stop()

URL_TRIPS = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
URL_EXPENSES = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

df_trips = pd.DataFrame()
df_expenses = pd.DataFrame()

# Fetch Trips Database
r_trips = requests.get(f"{URL_TRIPS}?ts={time.time()}", headers=HEADERS)
if r_trips.status_code == 200:
    content_trips = base64.b64decode(r_trips.json()["content"]).decode("utf-8")
    df_trips = pd.read_csv(io.StringIO(content_trips))
    if not df_trips.empty:
        df_trips['Clean_Date'] = pd.to_datetime(df_trips['Date']).dt.date

# Fetch Expenses Database
r_expenses = requests.get(f"{URL_EXPENSES}?ts={time.time()}", headers=HEADERS)
if r_expenses.status_code == 200:
    content_expenses = base64.b64decode(r_expenses.json()["content"]).decode("utf-8")
    df_expenses = pd.read_csv(io.StringIO(content_expenses))
    if not df_expenses.empty:
        df_expenses['Clean_Date'] = pd.to_datetime(df_expenses['Date']).dt.date

if not df_trips.empty:
    st.markdown("### 🗓️ Select Settlement Frame Window")
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("From Date", min(df_trips['Clean_Date']), key="s_start")
    with col2: end_date = st.date_input("To Date", max(df_trips['Clean_Date']), key="s_end")
        
    filtered_trips = df_trips[(df_trips['Clean_Date'] >= start_date) & (df_trips['Clean_Date'] <= end_date)]
    
    with st.expander(f"📱 View Logged Travel History ({len(filtered_trips)} Days)", expanded=False):
        st.dataframe(filtered_trips.sort_values(by="Clean_Date", ascending=False), use_container_width=True, hide_index=True)
        
    # Isolate calculation layers
    carpool_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
    other_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
    
    # 1. PROCESS DAILY CARPOOL LOGS
    for _, row in filtered_trips.iterrows():
        driver_matched = str(row['Driver']).strip().title()
        if driver_matched not in commuters: continue
        
        full_p = [p.strip().title() for p in str(row['Full Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        half_p = [p.strip().title() for p in str(row['Half Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        
        for p in full_p:
            if p in commuters and p != driver_matched:
                carpool_debts[p][driver_matched] += 300.0
        for p in half_p:
            if p in commuters and p != driver_matched:
                carpool_debts[p][driver_matched] += 150.0

    # 2. PROCESS OTHER SHAPED SYSTEM BILLS
    total_period_expenses = 0.0
    filtered_expenses = pd.DataFrame()
    
    if not df_expenses.empty:
        filtered_expenses = df_expenses[(df_expenses['Clean_Date'] >= start_date) & (df_expenses['Clean_Date'] <= end_date)]
        
        if not filtered_expenses.empty:
            total_period_expenses = filtered_expenses['Total Amount'].sum()
            
            for _, row in filtered_expenses.iterrows():
                payer = str(row['Paid By']).strip().title()
                per_head = float(row['Per Head Cost'])
                consumers = [p.strip().title() for p in str(row['Shared By']).split(',') if p.strip()]
                
                for p in consumers:
                    if p in commuters and p != payer:
                        other_debts[p][payer] += per_head

    # 3. CALCULATE CARPOOL MATRICES SETTLEMENTS
    cp_settlements = []
    for i in range(len(commuters)):
        for j in range(i + 1, len(commuters)):
            p1, p2 = commuters[i], commuters[j]
            p1_owes = carpool_debts[p1][p2]
            p2_owes = carpool_debts[p2][p1]
            
            if p1_owes > p2_owes:
                net = p1_owes - p2_owes
                if net > 0: cp_settlements.append({"From": p1, "To": p2, "Amount": net})
            elif p2_owes > p1_owes:
                net = p2_owes - p1_owes
                if net > 0: cp_settlements.append({"From": p2, "To": p1, "Amount": net})

    # 4. CALCULATE INDEPENDENT EXPENSE SETTLEMENTS
    misc_settlements = []
    for i in range(len(commuters)):
        for j in range(i + 1, len(commuters)):
            p1, p2 = commuters[i], commuters[j]
            p1_owes = other_debts[p1][p2]
            p2_owes = other_debts[p2][p1]
            
            if p1_owes > p2_owes:
                net = p1_owes - p2_owes
                if net > 0: misc_settlements.append({"From": p1, "To": p2, "Amount": net})
            elif p2_owes > p1_owes:
                net = p2_owes - p1_owes
                if net > 0: misc_settlements.append({"From": p2, "To": p1, "Amount": net})

    # --- DISPLAY BLOCK 1: CARPOOL ---
    st.markdown("### 🚗 1. Carpool Travel Settlements")
    if cp_settlements:
        for s in cp_settlements:
            st.markdown(f"""
            <div class="mobile-card">
                <span class="badge-carpool">₹{s['Amount']:.2f}</span>
                <div style="font-weight:700; color:#F8FAFC;">👉 {s['From']}</div>
                <div style="font-size:13px; color:#94A3B8; margin-top:4px;">Owes travel fees to <b>{s['To']}</b></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No carpool payout dues across this frame window.")

    # --- DISPLAY BLOCK 2: EXPENSES ---
    st.markdown("### 🍔 2. Other Expense Settlements")
    if misc_settlements:
        for s in misc_settlements:
            st.markdown(f"""
            <div class="mobile-card">
                <span class="badge-expense">₹{s['Amount']:.2f}</span>
                <div style="font-weight:700; color:#F8FAFC;">👉 {s['From']}</div>
                <div style="font-size:13px; color:#94A3B8; margin-top:4px;">Owes expense share to <b>{s['To']}</b></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No miscellaneous shared bills dues across this frame window.")
        
    # --- LIVE LEDGER REPLACEMENT ENGINE ---
    st.markdown("---")
    st.markdown(f"### 📋 Split Expense Settlement History (Window Total: ₹{total_period_expenses:,.2f})")
    if not filtered_expenses.empty:
        # Display the actual raw bill parameters instead of the old graphs
        display_exp_df = filtered_expenses[['Date', 'Paid By', 'Total Amount', 'Description', 'Shared By', 'Per Head Cost']].copy()
        st.dataframe(
            display_exp_df.sort_values(by="Date", ascending=False), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No custom shared bills recorded within this selected date window.")
        
    # --- WHATSAPP TEXT FORMATTER ---
    whatsapp_text = f"🚗 *Carpool Dues Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
    if cp_settlements:
        for s in cp_settlements: 
            whatsapp_text += f"• *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.2f}*\n"
    else:
        whatsapp_text += "_All carpool accounts clear_\n"
        
    whatsapp_text += "\n🍔 *Other Expenses Summary:* \n"
    if misc_settlements:
        for s in misc_settlements: 
            whatsapp_text += f"• *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.2f}*\n"
    else:
        whatsapp_text += "_No miscellaneous dues_\n"
        
    whatsapp_text += "--------------------------------------"
    
    encoded_text = urllib.parse.quote(whatsapp_text)
    whatsapp_url = f"https://wa.me/?text={encoded_text}"
    
    st.markdown(f"""
        <a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">
            💬 SHARE DIRECT TO WHATSAPP GROUP
        </a>
    """, unsafe_allow_html=True)
else:
    st.info("Log database file is empty.")
