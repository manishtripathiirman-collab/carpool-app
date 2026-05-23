import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime
import os

# --- MOBILE-FIRST WINDOW CONFIGURATION ---
st.set_page_config(page_title="MG Payout Engine", page_icon="💰", layout="centered")

# --- MATCHING CYBERPUNK DARK THEME ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.95)), 
                          url('https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=800&q=80');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .mobile-card {
        background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 16px; margin-bottom: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); border: 1px solid rgba(244, 63, 94, 0.25);
    }
    .badge-payout {
        background-color: rgba(244, 63, 94, 0.15); color: #FB7185;
        padding: 6px 14px; border-radius: 10px; font-size: 18px; font-weight: 800; float: right;
    }
    .mobile-title {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 26px !important; font-weight: 800; color: #FFFFFF;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
    }
    label, p, span { color: #CBD5E1 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">💰 Settlement Panel</p>', unsafe_allow_html=True)
st.caption("Fetches mobile inputs automatically to calculate strict net transfers.")

commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]
DATA_FILE = "carpool_logs.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['Clean_Date'] = pd.to_datetime(df['Date']).dt.date
    
    # --- DATE WINDOW SELECTOR ---
    st.markdown("### 🗓️ Select Settlement Frame Window")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", min(df['Clean_Date']))
    with col2:
        end_date = st.date_input("To Date", max(df['Clean_Date']))
        
    filtered_df = df[(df['Clean_Date'] >= start_date) & (df['Clean_Date'] <= end_date)]
    
    with st.expander(f"📱 View Logged Travel History ({len(filtered_df)} Days)"):
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
    # --- LOGIC SETTLEMENT ENGINE ---
    raw_debts = defaultdict(lambda: defaultdict(float))
    
    for _, row in filtered_df.iterrows():
        if row['Clean_Date'].weekday() in [5, 6]:
            continue # Automatic weekend skipping
            
        driver = row['Driver']
        
        # Parse passenger lists out of string cells
        full_p = [p.strip() for p in str(row['Full Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        half_p = [p.strip() for p in str(row['Half Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        
        for p in full_p:
            if p in commuters and p != driver:
                raw_debts[p][driver] += 300.0
                
        for p in half_p:
            if p in commuters and p != driver:
                raw_debts[p][driver] += 150.0

    # Netting calculations
    settlements = []
    for i in range(len(commuters)):
        for j in range(i + 1, len(commuters)):
            p1, p2 = commuters[i], commuters[j]
            p1_owes, p2_owes = raw_debts[p1][p2], raw_debts[p2][p1]
            
            if p1_owes > p2_owes:
                net = p1_owes - p2_owes
                if net > 0: settlements.append({"From": p1, "To": p2, "Amount": net})
            elif p2_owes > p1_owes:
                net = p2_owes - p1_owes
                if net > 0: settlements.append({"From": p2, "To": p1, "Amount": net})

    # --- SHOW MOBILE CARDS ---
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
            
        # Copy-ready clipboard block
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("🟢 **Copy for WhatsApp Group Chat:**")
        whatsapp_text = f"*🚗 Carpool Settlement Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
        whatsapp_text += "--------------------------------------\n"
        for s in settlements:
            whatsapp_text += f"👉 *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.0f}*\n"
        whatsapp_text += "--------------------------------------\n"
        st.code(whatsapp_text, language="text")
    else:
        st.success("🎉 All accounts match perfectly across this window!")
else:
    st.info("Log database is empty. Please save a few daily entries using your Mobile Logger app first.")
