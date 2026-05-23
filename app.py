import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime
import io

# --- WINDOW THEME CONFIGURATION ---
st.set_page_config(
    page_title="Mission Gurgaon | Carpool Ledger", 
    page_icon="🚗", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN DESIGN SYSTEM (CUSTOM CSS WITH BACKGROUND IMAGE) ---
st.markdown("""
    <style>
    /* Premium Background Image Configuration */
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                          url('https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Sleek Translucent Cards for Content Containers */
    div.element-container:has(div.stTextArea), div.element-container:has(div.stDateInput), .stExpander {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Typography Overrides */
    .app-title { 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 32px !important; 
        font-weight: 700; 
        color: #1E3A8A;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
    }
    
    .section-header {
        font-size: 18px !important;
        font-weight: 600;
        color: #1F2937;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    /* Clean DataFrame Styling Override */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- TITLE HEADER ---
st.markdown('<p class="app-title">🚗 Mission Gurgaon Commute Ledger</p>', unsafe_allow_html=True)
st.caption("A premium cloud-connected ledger for effortless carpool settlements.")

# --- INITIALIZE GROUP PROFILES ---
if "commuters" not in st.session_state:
    st.session_state.commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]

# --- LAYOUT CARDS: STEP 1 ---
st.markdown('<p class="section-header">📋 Step 1: Paste Google Sheet Logs</p>', unsafe_allow_html=True)
pasted_text = st.text_area(
    "Select your columns (Date, Driver, Full, Half) inside Google Sheets, copy them, and drop them here:", 
    height=130, 
    placeholder="Date\tDriver\tFull Day Passengers\tHalf Day Passengers...",
    label_visibility="collapsed"
)

if pasted_text.strip():
    try:
        # Read clipboard structure
        df = pd.read_csv(io.StringIO(pasted_text), sep="\t")
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        date_col = next((c for c in df.columns if 'date' in c), None)
        driver_col = next((c for c in df.columns if 'driver' in c), None)
        full_col = next((c for c in df.columns if 'full' in c or 'passenger' in c and 'half' not in c), None)
        half_col = next((c for c in df.columns if 'half' in c or 'am' in c or 'pm' in c), None)
        
        if not date_col or not driver_col:
            st.error("⚠️ Header Row Missing: Please make sure you copy the top title row from your Google Sheet.")
            st.stop()
            
        df['Clean_Date'] = pd.to_datetime(df[date_col], errors='coerce').dt.date
        df = df.dropna(subset=['Clean_Date'])
        
        # --- LAYOUT CARDS: STEP 2 ---
        st.markdown('<p class="section-header">🗓️ Step 2: Choose Billing Window</p>', unsafe_allow_html=True)
        min_date = min(df['Clean_Date'])
        max_date = max(df['Clean_Date'])
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("Start Boundary Date", min_date)
        with col_d2:
            end_date = st.date_input("End Boundary Date", max_date)
            
        filtered_df = df[(df['Clean_Date'] >= start_date) & (df['Clean_Date'] <= end_date)]
        
        with st.expander(f"👀 View Verified Data Sheet ({len(filtered_df)} working days detected)", expanded=False):
            st.dataframe(filtered_df, use_container_width=True)
        
        # --- LOGIC PROCESSING ENGINE ---
        raw_debts = defaultdict(lambda: defaultdict(float))
        
        for _, row in filtered_df.iterrows():
            if row['Clean_Date'].weekday() in [5, 6]:
                continue # Ignore weekends
                
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

        # Netting Engine
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
                    if net > 0: settlements.append({"From": p2, "To": p1, "Amount": net})

        # --- LAYOUT CARDS: STEP 3 (RESULTS) ---
        st.markdown('<p class="section-header">💰 Step 3: Net Cash Settlements</p>', unsafe_allow_html=True)
        
        if settlements:
            settlement_df = pd.DataFrame(settlements)
            display_df = settlement_df.copy()
            display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹ {x:,.0f}")
            
            col_table, col_wa = st.columns([4, 5], gap="large")
            
            with col_table:
                st.markdown("**Direct Pair-Wise Payout Table**")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
            with col_wa:
                st.markdown("**📲 Copy Ready for WhatsApp Group Chat**")
                whatsapp_text = f"*🚗 Carpool Settlement Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
                whatsapp_text += "--------------------------------------\n"
                for s in settlements:
                    whatsapp_text += f"👉 *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.0f}*\n"
                whatsapp_text += "--------------------------------------\n"
                whatsapp_text += "💡 _Settlements calculated strictly direct peer-to-peer._"
                
                st.code(whatsapp_text, language="text")
        else:
            st.success("🎉 Parity reached! All accounts match up perfectly across this window.")
            
    except Exception as e:
        st.error(f"Error parsing text structure layout. Make sure you select clean columns. Details: {e}")
else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Awaiting input details. Copy your spreadsheet logs row matrix and paste them into Step 1 above to run calculation pipelines.")
