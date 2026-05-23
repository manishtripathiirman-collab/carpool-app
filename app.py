import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime
import io

# --- MOBILE-FIRST WINDOW CONFIGURATION ---
st.set_page_config(
    page_title="MG Ledger", 
    page_icon="🚗", 
    layout="centered", # Dynamic narrowing for mobile viewports
    initial_sidebar_state="collapsed"
)

# --- ADVANCED MOBILE UI STYLING SYSTEM ---
st.markdown("""
    <style>
    /* Premium Minimalist Travel Background */
    .stApp {
        background-image: linear-gradient(rgba(244, 246, 249, 0.92), rgba(244, 246, 249, 0.92)), 
                          url('https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=800&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Native Smartphone App Cards */
    .mobile-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid #E5E7EB;
    }
    
    /* WhatsApp Copy Panel */
    .whatsapp-container {
        background: #E8F7F0 !important;
        border-radius: 16px;
        padding: 16px;
        border-left: 6px solid #25D366;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.08);
    }
    
    /* Elegant Micro Badges */
    .badge-driver {
        background-color: #EFF6FF;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-payout {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 700;
        float: right;
    }
    
    /* Clean Mobile Text Utilities */
    .mobile-title {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 26px !important;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.5px;
    }
    .card-name {
        font-size: 16px;
        font-weight: 700;
        color: #1F2937;
    }
    .card-sub {
        font-size: 13px;
        color: #6B7280;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOBILE APP HEADER ---
st.markdown('<p class="mobile-title">🚗 Mission Gurgaon</p>', unsafe_allow_html=True)
st.caption("Tap, paste, and instantly resolve pairwise group ride expenses.")

# --- INITIALIZE GROUP PROFILES ---
if "commuters" not in st.session_state:
    st.session_state.commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]

# --- STEP 1: MOBILE PASTE PANEL ---
st.markdown("### 📋 Step 1: Import Sheets Log")
pasted_text = st.text_area(
    "Tap here and paste data rows from your Google Sheets mobile app:", 
    height=120, 
    placeholder="Tap to paste spreadsheet rows...",
    label_visibility="collapsed"
)

if pasted_text.strip():
    try:
        # Load and cleanly digest strings
        df = pd.read_csv(io.StringIO(pasted_text), sep="\t")
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        date_col = next((c for c in df.columns if 'date' in c), None)
        driver_col = next((c for c in df.columns if 'driver' in c), None)
        full_col = next((c for c in df.columns if 'full' in c or 'passenger' in c and 'half' not in c), None)
        half_col = next((c for c in df.columns if 'half' in c or 'am' in c or 'pm' in c), None)
        
        if not date_col or not driver_col:
            st.error("⚠️ Header Missing: Please make sure you copy the top title header row from your sheet.")
            st.stop()
            
        df['Clean_Date'] = pd.to_datetime(df[date_col], errors='coerce').dt.date
        df = df.dropna(subset=['Clean_Date'])
        
        # --- STEP 2: MOBILE DATE SELECTION SLIDERS ---
        st.markdown("### 🗓️ Step 2: Set Billing Period")
        min_date = min(df['Clean_Date'])
        max_date = max(df['Clean_Date'])
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("From:", min_date)
        with col_d2:
            end_date = st.date_input("To:", max_date)
            
        filtered_df = df[(df['Clean_Date'] >= start_date) & (df['Clean_Date'] <= end_date)]
        
        # Collapse massive overview matrices behind a clean mobile drawer widget
        with st.expander(f"📱 View Verified Travel Log ({len(filtered_df)} Days)"):
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # --- CALCULATION ENGINE ---
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

        # Netting Engine processing 
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

        # --- STEP 3: NATIVE MOBILE CARD RENDER ---
        st.markdown("### 💰 Step 3: Final Pair-Wise Transfers")
        
        if settlements:
            # Render individual cards built for phone viewports
            for s in settlements:
                st.markdown(f"""
                <div class="mobile-card">
                    <span class="badge-payout">₹{s['Amount']:.0f}</span>
                    <div class="card-name">👉 {s['From']}</div>
                    <div class="card-sub">Owes money directly to <b>{s['To']}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
            # Render WhatsApp block below
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📲 Copy Ready for WhatsApp Group Chat**")
            
            whatsapp_text = f"*🚗 Carpool Settlement Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
            whatsapp_text += "--------------------------------------\n"
            for s in settlements:
                whatsapp_text += f"👉 *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.0f}*\n"
            whatsapp_text += "--------------------------------------\n"
            whatsapp_text += "💡 _Open link to compute custom dates._"
            
            st.code(whatsapp_text, language="text")
        else:
            st.success("🎉 Parity reached! All accounts match up perfectly across this window.")
            
    except Exception as e:
        st.error(f"Error parsing rows. Double check your sheet's top header layout selection row. Details: {e}")
else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Awaiting input logs. Open your Google Sheet app, copy your target row blocks, and paste them right into Step 1 above.")
