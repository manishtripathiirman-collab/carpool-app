import streamlit as st
import pandas as pd
import datetime
import requests
import base64
import io
import urllib.parse

st.set_page_config(page_title="MG Payout Engine", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.95)), 
                          url('https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=800&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-card { background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(10px); border-radius: 16px; padding: 16px; margin-bottom: 12px; border: 1px solid rgba(244, 63, 94, 0.25); }
    .badge-payout { background-color: rgba(244, 63, 94, 0.15); color: #FB7185; padding: 6px 14px; border-radius: 10px; font-size: 18px; font-weight: 800; float: right; }
    .mobile-title { font-family: sans-serif; font-size: 26px !important; font-weight: 800; color: #FFFFFF; }
    label, p, span { color: #CBD5E1 !important; }
    
    /* WhatsApp Button Styling */
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
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">💰 Settlement Panel</p>', unsafe_allow_html=True)

commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")
URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

if not TOKEN or not REPO:
    st.info("💡 Awaiting cloud connection keys inside secrets panel.")
    st.stop()

live_url = f"{URL}?timestamp={datetime.datetime.now().timestamp()}"
r = requests.get(live_url, headers=HEADERS)

if r.status_code == 200:
    content = base64.b64decode(r.json()["content"]).decode("utf-8")
    df = pd.read_csv(io.StringIO(content))
    df['Clean_Date'] = pd.to_datetime(df['Date']).dt.date
    
    st.markdown("### 🗓️ Select Settlement Frame Window")
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("From Date", min(df['Clean_Date']))
    with col2: end_date = st.date_input("To Date", max(df['Clean_Date']))
        
    filtered_df = df[(df['Clean_Date'] >= start_date) & (df['Clean_Date'] <= end_date)]
    
    with st.expander(f"📱 View Logged Travel History ({len(filtered_df)} Days)", expanded=False):
        st.dataframe(filtered_df.sort_values(by="Clean_Date", ascending=False), use_container_width=True, hide_index=True)
        
    ledger_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
    
    for _, row in filtered_df.iterrows():
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
                <span class="badge-payout">₹{s['Amount']:.0f}</span>
                <div style="font-weight:700; color:#F8FAFC;">👉 {s['From']}</div>
                <div style="font-size:13px; color:#94A3B8; margin-top:4px;">Owes cash directly to <b>{s['To']}</b></div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- GENERATE THE WHATSAPP MESSAGE TEXT ---
        whatsapp_text = f"🚗 *Carpool Settlement Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
        whatsapp_text += "--------------------------------------\n"
        for s in settlements: 
            whatsapp_text += f"👉 *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.0f}*\n"
        whatsapp_text += "--------------------------------------"
        
        # URL encode the text safely so spaces/emojis pass smoothly to WhatsApp
        encoded_text = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me/?text={encoded_text}"
        
        # --- NEW: ONE-CLICK NATIVE WHATSAPP ACTION BUTTON ---
        st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">
                💬 SHARE DIRECT TO WHATSAPP GROUP
            </a>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 View Raw Code Copy Alternative"):
            st.code(whatsapp_text, language="text")
    else:
        st.success("🎉 All accounts match perfectly across this window!")
else:
    st.info("Log database file is empty.")
