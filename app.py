import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime
import io

# --- MOBILE-FIRST WINDOW CONFIGURATION ---
st.set_page_config(
    page_title="MG Ledger", 
    page_icon="🚗", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- NEON-DARK AUTOMOTIVE PREMIUM DESIGN SYSTEM ---
st.markdown("""
    <style>
    /* Deep Dark Moody Highway Background */
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.95)), 
                          url('https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=800&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Premium Glassmorphism Dark Cards with Cyber Neon Borders */
    div.element-container:has(div.stTextArea), div.element-container:has(div.stDateInput), .stExpander {
        background: rgba(30, 41, 59, 0.70) !important;
        backdrop-filter: blur(12px);
        border-radius: 16px !important;
        padding: 12px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        border: 1px solid rgba(99, 102, 241, 0.25) !important; /* Subtle Neon Indigo border */
    }
    
    /* Native Smartphone App Cards for Settlements */
    .mobile-card {
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(244, 63, 94, 0.25); /* Glowing Rose Border */
    }
    
    /* High-Contrast Cyber Badges */
    .badge-payout {
        background-color: rgba(244, 63, 94, 0.15);
        color: #FB7185;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 18px;
        font-weight: 800;
        float: right;
        border: 1px solid rgba(244, 63, 94, 0.3);
    }
    
    /* Luminous WhatsApp Integration Box */
    .whatsapp-container {
        background: rgba(16, 185, 129, 0.1) !important;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Vibrant Electric Typography */
    .mobile-title {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 28px !important;
        font-weight: 800;
        color: #FFFFFF;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
        letter-spacing: -0.5px;
    }
    
    .section-header {
        color: #E2E8F0 !important;
        font-size: 16px !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .card-name {
        font-size: 16px;
        font-weight: 700;
        color: #F8FAFC;
    }
    .card-sub {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Override standard input text colors to fit dark theme */
    label, p, span {
        color: #CBD5E1 !important;
    }
    textarea {
        color: #FFFFFF !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOBILE APP HEADER ---
st.markdown('<p class="mobile-title">🚗 Mission Gurgaon</p>', unsafe_allow_html=True)
st.caption("A premium cyberpunk-styled carpool engine for direct pairwise netting.")

# --- INITIALIZE GROUP PROFILES ---
if "commuters" not in st.session_state:
    st.session_state.commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]

# --- STEP 1: MOBILE PASTE PANEL ---
st.markdown('<p class="section-header">📋 STEP 1: IMPORT SHEET DATA</p>', unsafe_allow_html=True)
pasted_text = st.text_area(
    "Tap here and paste data rows from your Google Sheets mobile app:", 
    height=120, 
    placeholder="Tap to paste spreadsheet rows here...",
    label_visibility="collapsed"
)

if pasted_text.strip():
    try:
        # Process the pasted spreadsheet chunk
        df = pd.read_csv(io.StringIO(pasted_text), sep="\t")
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        date_col = next((c for c in df.columns if 'date' in c), None)
        driver_col = next((c for c in df.columns if 'driver' in c), None)
        full_col = next((c for c in df.columns if 'full' in c or 'passenger' in c and 'half' not in c), None)
        half_col = next((c for c in df.columns if 'half' in c or 'am' in c or 'pm' in c), None)
        
        if not date_col or not driver_col:
            st.error("⚠️ Header Missing: Please remember to copy the top title row from your sheet.")
            st.stop()
            
        df['Clean_Date'] = pd.to_datetime(df[date_col], errors='coerce').dt.date
        df = df.dropna(subset=['Clean_Date'])
        
        # --- STEP 2: MOBILE DATE SELECTION SLIDERS ---
        st.markdown('<p class="section-header">🗓️ STEP 2: SET BILLING TIMEFRAME</p>', unsafe_allow_html=True)
        min_date = min(df['Clean_Date'])
        max_date = max(df['Clean_Date'])
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("From:", min_date)
        with col_d2:
            end_date = st.date_input("To:", max_date)
            
        filtered_df = df[(df['Clean_Date'] >= start_date) & (df['Clean_Date'] <= end_date)]
        
        with st.expander(f"📱 View Parsed Roster Rows ({len(filtered_df)} Days)"):
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # --- LOGIC CALCULATION ENGINE ---
        raw_debts = defaultdict(lambda: defaultdict(float))
        
        for _, row in filtered_df.iterrows():
            if row['Clean_Date'].weekday() in [5, 6]:
                continue
                
            driver_raw = str(row[driver_col]).strip()
            driver = next((c for c in st.session_state.commuters if c.lower() in driver_raw.lower()), None)
            
            if not driver:
                continue
                
            full_passengers = []
            if full_col and full_col in row and pd.notna(row[full_col]):
                full_txt = str(row[full_col])
                for m in st.session_state.commuters:
                    if m.lower() in full_txt.lower() and m != driver: full_passengers.append(m)
                        
            half_passengers = []
            if half_col and half_col in row and pd.notna(row[half_col]):
                half_txt = str(row[half_col])
                for m in st.session_state.commuters:
                    if m.lower() in half_txt.lower() and m != driver: half_passengers.append(m)
                        
            for p in full_passengers:
                if p in half_passengers: half_passengers.remove(p)
                
            for p in full_passengers: raw_debts[p][driver] += 300.0
            for p in half_passengers: raw_debts[p][driver] += 150.0

        # Run netting mechanics
        all_members = st.session_state.commuters
        settlements = []
        for i in range(len(all_members)):
            for j in range(i + 1, len(all_members)):
                p1, p2 = all_members[i], all_members[j]
                p1_owes, p2_owes = raw_debts[p1][p2], raw_debts[p2][p1]
                
                if p1_owes > p2_owes:
                    net = p1_owes - p2_owes
                    if net > 0: settlements.append({"From": p1, "To": p2, "Amount": net})
                elif p2_owes > p1_owes:
                    net = p2_owes - p1_owes
                    if net > 0: settlements.append({"From":
