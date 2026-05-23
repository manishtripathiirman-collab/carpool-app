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

# --- CUSTOM CSS FOR BETTER VISUALS ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: 600; color: #1E3A8A; }
    .whatsapp-box { background-color: #E7F5EE; padding: 15px; border-radius: 8px; border-left: 5px solid #25D366; }
    .metric-box { background-color: #F3F4F6; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #E5E7EB; }
    </style>
""", unsafe_allow_html=True)

# --- TITLE HEADER ---
st.markdown('<p class="big-font">🚗 Mission Gurgaon Commute Ledger</p>', unsafe_allow_html=True)
st.caption("Calculate fares and direct person-to-person settlements cleanly.")

# --- INITIALIZE GROUP PROFILES ---
if "commuters" not in st.session_state:
    st.session_state.commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]

# --- LAYOUT CARDS: STEP 1 ---
st.markdown("### 📋 Step 1: Paste Sheet Logs")
with st.expander("📂 Click here to open and paste your Google Sheet rows", expanded=True):
    pasted_text = st.text_area(
        "Select your columns (Date, Driver, Full, Half) inside Google Sheets, copy them, and drop them here:", 
        height=140, 
        placeholder="Date\tDriver\tFull Day Passengers\tHalf Day Passengers..."
    )

if pasted_text.strip():
    try:
        # Read clip data structures
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
        st.markdown("### 🗓️ Step 2: Choose Billing Window")
        min_date = min(df['Clean_Date'])
        max_date = max(df['Clean_Date'])
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("Start Boundary Date", min_date)
        with col_d2:
            end_date = st.date_input("End Boundary Date", max_date)
            
        filtered_df = df[(df['Clean_Date'] >= start_date) & (df['Clean_Date'] <= end_date)]
        
        # Display clean preview table with metric counts
        with st.expander(f"👀 View Roster Preview Matrix ({len(filtered_df)} working days detected)"):
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
        st.markdown("### 💰 Step 3: Net Cash Settlements")
        
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
    # Stylized informational box when application is empty
    st.info("💡 Awaiting input details. Copy your spreadsheet logs row matrix and paste them into Step 1 above to run calculation pipelines.")import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime
import io

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Mission Gurgaon Copypaste Ledger", page_icon="🚗", layout="wide")
st.title("🚗 Google Sheets Data Paste Carpool Ledger")
st.markdown("Bypass browser security. Simply copy your data rows from Google Sheets and paste them below.")

# --- INITIALIZE GROUP PROFILES ---
if "commuters" not in st.session_state:
    st.session_state.commuters = ["Manish Tripathi", "Abhishek Chaudhary", "Dk Maurya", "Ajay Nair", "Ankit Kapoor"]

with st.sidebar:
    st.header("👥 Group Profiles")
    st.write("Tracked Members:", ", ".join(st.session_state.commuters))
    st.markdown("---")
    st.caption("Standard Rates:\n- Full Day: ₹300\n- Half Day: ₹150\n- Driver/Absent: ₹0")

# --- STEP 1: DATA PASTE CONTAINER ---
st.header("📋 Step 1: Paste Your Google Sheet Rows")
st.markdown("Go to your Google Sheet, select the data rows (including your header row), copy them, and paste them right here:")

pasted_text = st.text_area("Paste here directly from your spreadsheet:", height=200, placeholder="Date\tDriver\tFull Day Passengers\tHalf Day Passengers...")

if pasted_text.strip():
    try:
        # Read the tab-separated values from the clipboard paste
        df = pd.read_csv(io.StringIO(pasted_text), sep="\t")
        
        # Clean up headers (remove accidental spaces and make lowercase)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Dynamically locate columns
        date_col = next((c for c in df.columns if 'date' in c), None)
        driver_col = next((c for c in df.columns if 'driver' in c), None)
        full_col = next((c for c in df.columns if 'full' in c or 'passenger' in c and 'half' not in c), None)
        half_col = next((c for c in df.columns if 'half' in c or 'am' in c or 'pm' in c), None)
        
        if not date_col or not driver_col:
            st.error("Error: Could not locate 'Date' or 'Driver' columns. Ensure you copied your header row from the sheet.")
            st.stop()
            
        # Standardize dates and clear out empty formatting rows
        df['Clean_Date'] = pd.to_datetime(df[date_col], errors='coerce').dt.date
        df = df.dropna(subset=['Clean_Date'])
        
        # --- STEP 2: DATE RANGE FILTER ---
        st.header("🗓️ Step 2: Select Calculation Timeframe Window")
        min_date = min(df['Clean_Date'])
        max_date = max(df['Clean_Date'])
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("Start Date", min_date)
        with col_d2:
            end_date = st.date_input("End Date", max_date)
            
        # Filter data matrix
        filtered_df = df[(df['Clean_Date'] >= start_date) & (df['Clean_Date'] <= end_date)]
        
        st.subheader("📝 Processed Trip Records Preview")
        st.dataframe(filtered_df, use_container_width=True)
        
        # --- STEP 3: LOGIC CALCULATION ENGINE ---
        raw_debts = defaultdict(lambda: defaultdict(float))
        
        for _, row in filtered_df.iterrows():
            if row['Clean_Date'].weekday() in [5, 6]:
                continue  # Skip weekends
                
            driver_raw = str(row[driver_col]).strip()
            driver = next((c for c in st.session_state.commuters if c.lower() in driver_raw.lower()), None)
            
            if not driver:
                continue
                
            # Parse Full Day Passengers
            full_passengers = []
            if full_col and full_col in row and pd.notna(row[full_col]):
                full_txt = str(row[full_col])
                for member in st.session_state.commuters:
                    if member.lower() in full_txt.lower() and member != driver:
                        full_passengers.append(member)
                        
            # Parse Half Day Passengers
            half_passengers = []
            if half_col and half_col in row and pd.notna(row[half_col]):
                half_txt = str(row[half_col])
                for member in st.session_state.commuters:
                    if member.lower() in half_txt.lower() and member != driver:
                        half_passengers.append(member)
                        
            # Fix overlaps
            for p in full_passengers:
                if p in half_passengers: half_passengers.remove(p)
                
            # Accumulate values
            for p in full_passengers: raw_debts[p][driver] += 300.0
            for p in half_passengers: raw_debts[p][driver] += 150.0

        # --- STEP 4: STRICT PAIR-WISE NETTING ---
        all_members = st.session_state.commuters
        settlements = []
        
        for i in range(len(all_members)):
            for j in range(i + 1, len(all_members)):
                p1 = all_members[i]
                p2 = all_members[j]
                
                p1_owes_p2 = raw_debts[p1][p2]
                p2_owes_p1 = raw_debts[p2][p1]
                
                if p1_owes_p2 > p2_owes_p1:
                    net = p1_owes_p2 - p2_owes_p1
                    if net > 0: settlements.append({"From": p1, "To": p2, "Amount": net})
                elif p2_owes_p1 > p1_owes_p2:
                    net = p2_owes_p1 - p1_owes_p2
                    if net > 0: settlements.append({"From": p2, "To": p1, "Amount": net})

        # --- RENDER RESULTS ---
        st.header("💰 Net Pair-Wise Settlements")
        if settlements:
            settlement_df = pd.DataFrame(settlements)
            display_df = settlement_df.copy()
            display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹ {x:,.2f}")
            st.table(display_df)
            
            st.subheader("📋 Output Summary for WhatsApp Group")
            whatsapp_text = f"*Carpool Settlement Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
            for s in settlements:
                whatsapp_text += f"👉 *{s['From']}* pays *{s['To']}*: ₹{s['Amount']:.0f}\n"
            st.code(whatsapp_text, language="text")
        else:
            st.success("🎉 Parity reached! All accounts match up perfectly across this window.")
            
    except Exception as e:
        st.error(f"Error parsing pasted text. Ensure you selected clean rows from Google Sheets. Details: {e}")
else:
    st.info("Awaiting input. Copy data rows from your Google Sheet and paste them into the box above.")
