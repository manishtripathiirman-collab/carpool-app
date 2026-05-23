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
    .whatsapp-btn { display: flex; align-items: center; justify-content: center; background-color: #25D366 !important; color: white !important; font-weight: 700; font-size: 16px; text-decoration: none; padding: 14px; border-radius: 12px; width: 100%; text-align: center; margin-top: 15px; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3); }
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

df_trips, df_expenses = pd.DataFrame(), pd.DataFrame()

# Fetch Files with live cache breakers
r_trips = requests.get(f"{URL_TRIPS}?ts={time.time()}", headers=HEADERS)
if r_trips.status_code == 200:
    df_trips = pd.read_csv(io.StringIO(base64.b64decode(r_trips.json()["content"]).decode("utf-8")))
    if not df_trips.empty: df_trips['Clean_Date'] = pd.to_datetime(df_trips['Date']).dt.date

r_expenses = requests.get(f"{URL_EXPENSES}?ts={time.time()}", headers=HEADERS)
if r_expenses.status_code == 200:
    df_expenses = pd.read_csv(io.StringIO(base64.b64decode(r_expenses.json()["content"]).decode("utf-8")))
    if not df_expenses.empty: df_expenses['Clean_Date'] = pd.to_datetime(df_expenses['Date']).dt.date

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
    
    # Core separate ledgers
    carpool_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
    other_debts = {p1: {p2: 0.0 for p2 in commuters} for p1 in commuters}
    
    # Process Travel Logs
    for _, row in filtered_trips.iterrows():
        driver_matched = normalize_name(row['Driver'])
        if driver_matched not in commuters: continue
        full_p = [normalize_name(p) for p in str(row['Full Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        half_p = [normalize_name(p) for p in str(row['Half Day Passengers']).split(',') if p.strip() and p.strip() != "None"]
        for p in full_p:
            if p in commuters and p != driver_matched: carpool_debts[p][driver_matched] += 300.0
        for p in half_p:
            if p in commuters and p != driver_matched: carpool_debts[p][driver_matched] += 150.0

    # Process Split Expenses Logs
    total_period_expenses = 0.0
    filtered_expenses = pd.DataFrame()
    if not df_expenses.empty:
        filtered_expenses = df_expenses[(df_expenses['Clean_Date'] >= start_date) & (df_expenses['Clean_Date'] <= end_date)]
        if not filtered_expenses.empty:
            total_period_expenses = filtered_expenses['Total Amount'].sum()
            for _, row in filtered_expenses.iterrows():
                payer = normalize_name(row['Paid By'])
                per_head = float(row['Per Head Cost'])
                consumers = [normalize_name(p) for p in str(row['Shared By']).split(',') if p.strip()]
                for p in consumers:
                    if p in commuters and p != payer: other_debts[p][payer] += per_head

    # Calculate Pairs
    net_settlements = []
    for i in range(len(commuters)):
        for j in range(i + 1, len(commuters)):
            p1, p2 = commuters[i], commuters[j]
            
            cp_p1_owes = carpool_debts[p1][p2]
            cp_p2_owes = carpool_debts[p2][p1]
            
            misc_p1_owes = other_debts[p1][p2]
            misc_p2_owes = other_debts[p2][p1]
            
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

    tab_summary, tab_ledger = st.tabs(["💵 Payout Summary", "📋 Split Expense History"])

    with tab_summary:
        st.markdown("### 💎 Consolidated Net Pairwise Settlements")
        if net_settlements:
            for s in net_settlements:
                f_name = s["From"]
                t_name = s["To"]
                
                # Dynamic text builder for the clear sub-breakdown checklist row
                lines = []
                
                # Check Carpool positions
                if s["p1_cp_gross"] > 0 or s["p2_cp_gross"] > 0:
                    if s["p1_cp_gross"] > s["p2_cp_gross"]:
                        lines.append(f"• 🚗 **Carpool Dues:** {f_name} owes {t_name} **₹{s['p1_cp_gross'] - s['p2_cp_gross']:.0f}** (Net)")
                    elif s["p2_cp_gross"] > s["p1_cp_gross"]:
                        lines.append(f"• 🚗 **Carpool Dues:** {t_name} owes {f_name} **₹{s['p2_cp_gross'] - s['p1_cp_gross']:.0f}** (Net)")
                
                # Check Miscellaneous Expenses positions
                if s["p1_misc_gross"] > 0 or s["p2_misc_gross"] > 0:
                    if s["p1_misc_gross"] > s["p2_misc_gross"]:
                        lines.append(f"• 🍔 **Other Spend:** {f_name} owes {t_name} **₹{s['p1_misc_gross'] - s['p2_misc_gross']:.0f}** (Net)")
                    elif s["p2_misc_gross"] > s["p1_misc_gross"]:
                        lines.append(f"• 🍔 **Other Spend:** {t_name} owes {f_name} **₹{s['p2_misc_gross'] - s['p1_misc_gross']:.0f}** (Net)")

                breakdown_html = "<br>".join(lines) if lines else "• No individual segment debts."

                st.markdown(f"""
                <div class="mobile-card">
                    <div class="badge-payout">₹{s['Amount']:.2f}</div>
                    <div style="font-weight:700; font-size:16px; color:#F8FAFC;">👉 {f_name}</div>
                    <div style="font-size:13px; color:#94A3B8; margin-top:2px;">Owes net single payout directly to <b>{t_name}</b></div>
                    <div class="breakdown-text">
                        <b>📝 Itemized Calculations Breakup:</b><br>
                        {breakdown_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- CONSOLIDATED WHATSAPP OUTPUT ENGINE ---
            whatsapp_text = f"🚗 *Net Consolidated Payout Summary ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}):*\n"
            whatsapp_text += "--------------------------------------\n"
            for s in net_settlements:
                f_n, t_n = s["From"], s["To"]
                whatsapp_text += f"👉 *{f_n}* pays *{t_n}*:  *₹{s['Amount']:.2f}*\n"
                
                # Appends itemized lines cleanly to the text snippet string 
                if s["p1_cp_gross"] != s["p2_cp_gross"]:
                    cp_amt = s["p1_cp_gross"] - s["p2_cp_gross"]
                    whatsapp_text += f"   _↳ Carpool: {f_n if cp_amt > 0 else t_n} owes ₹{abs(cp_amt):.0f}_\n"
                if s["p1_misc_gross"] != s["p2_misc_gross"]:
                    misc_amt = s["p1_misc_gross"] - s["p2_misc_gross"]
                    whatsapp_text += f"   _↳ Other Bills: {f_n if misc_amt > 0 else t_n} owes ₹{abs(misc_amt):.0f}_\n"
                whatsapp_text += "\n"
            whatsapp_text += "--------------------------------------"
            
            st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(whatsapp_text)}" target="_blank" class="whatsapp-btn">💬 SHARE DIRECT TO WHATSAPP GROUP</a>', unsafe_allow_html=True)
        else:
            st.success("🎉 All accounts match up perfectly across this selected window!")

    with tab_ledger:
        st.markdown(f"### 📋 Full Bill Ledger Breakdown (Selected Window Total: ₹{total_period_expenses:,.2f})")
        if not filtered_expenses.empty:
            st.dataframe(filtered_expenses[['Date', 'Paid By', 'Total Amount', 'Description', 'Shared By', 'Per Head Cost']].sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else: st.info("No custom shared bills found within this selected date window.")
            
        st.markdown("---")
        with st.expander("📱 View Raw Travel Calendar Logs History"):
            st.dataframe(filtered_trips.sort_values(by="Clean_Date", ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("Log database file is empty.")
