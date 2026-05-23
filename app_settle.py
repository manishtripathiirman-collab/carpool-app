import streamlit as st
import datetime
import pandas as pd

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
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">💰 Settlement Panel</p>', unsafe_allow_html=True)

commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

# Core Data Source
mock_database = [
    {"Date": "2026-05-22", "Driver": "Manish", "Full Day Passengers": "Abhishek, Dk, Ajay, Ankit", "Half Day Passengers": "None"},
    {"Date": "2026-05-23", "Driver": "Manish", "Full Day Passengers": "Abhishek, Dk, Ajay, Ankit", "Half Day Passengers": "None"}
]

# --- VISUAL TRAVEL HISTORY LOGS PANEL ---
st.markdown("### 🗓️ Settlement Frame Window")
st.caption("Showing calculated dates from active ledger")

# Display the neat data table expander box
with st.expander("📱 View Logged Travel History (2 Days)", expanded=True):
    history_df = pd.DataFrame(mock_database)
    st.dataframe(history_df, use_container_width=True, hide_index=True)

# Set up clean baseline dictionary totals grid
ledger_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}

# Loop sequentially through the data to add totals
for entry in mock_database:
    dr = entry["Driver"]
    full_p = [p.strip() for p in entry["Full Day Passengers"].split(",") if p.strip() and p.strip() != "None"]
    half_p = [p.strip() for p in entry["Half Day Passengers"].split(",") if p.strip() and p.strip() != "None"]
    
    for p in full_p:
        if p in commuters and p != dr:
            ledger_debts[p][dr] += 300.0
    for p in half_p:
        if p in commuters and p != dr:
            ledger_debts[p][dr] += 150.0

# Netting cross calculations loops
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
    st.markdown("🟢 **Copy for WhatsApp Group Chat:**")
    whatsapp_text = f"*🚗 Carpool Settlement Summary (22 May - 23 May):*\n"
    whatsapp_text += "--------------------------------------\n"
    for s in settlements: 
        whatsapp_text += f"👉 *{s['From']}* pays *{s['To']}*:  *₹{s['Amount']:.0f}*\n"
    whatsapp_text += "--------------------------------------\n"
    st.code(whatsapp_text, language="text")
else:
    st.success("🎉 All accounts match perfectly across this window!")
