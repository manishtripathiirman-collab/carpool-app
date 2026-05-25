import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random
import urllib.parse

st.set_page_config(
    page_title="MG Settlement",
    page_icon="📊",
    layout="centered"
)

# --- CSS INJECTION LINES ---
st.markdown("<style>[data-testid='stAppViewContainer'] { background-color: #0F172A !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.block-container { background: rgba(30, 41, 59, 0.5) !important; padding: 20px !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; margin-top: 10px !important; margin-bottom: 20px !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.main-title { font-size: 24px !important; font-weight: 900; color: #FFFFFF !important; text-align: center; margin-bottom: 15px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.section-title { font-size: 14px !important; font-weight: 800; color: #94A3B8 !important; margin-top: 15px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-row { display: flex; gap: 10px; margin-bottom: 12px; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-box { flex: 1; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; text-align: center; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-label { font-size: 11px; font-weight: 800; color: #64748B; text-transform: uppercase; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-val { font-size: 15px; font-weight: 800; color: #F1F5F9; margin-top: 2px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-flex-card { background: linear-gradient(135deg, #064E3B, #022C22); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 14px; padding: 16px; margin-top: 15px; margin-bottom: 15px; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-flex-title { font-size: 12px !important; font-weight: 800 !important; color: #34D399 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-metric-num { font-size: 26px !important; font-weight: 900 !important; color: #FFFFFF !important; line-height: 1; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-metric-unit { font-size: 13px !important; color: #A7F3D0 !important; font-weight: 600; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-sub-text { font-size: 11px !important; color: #D1FAE5 !important; font-weight: 500; margin-top: 4px; opacity: 0.85; }</style>", unsafe_allow_html=True)
st.markdown("<style>div[data-testid='stPopover'] > button { background: rgba(52, 211, 153, 0.15) !important; color: #34D399 !important; border: 1px solid rgba(52, 211, 153, 0.3) !important; padding: 5px 12px !important; font-size: 11px !important; font-weight: 700 !important; border-radius: 8px !important; text-transform: uppercase !important; width: 100%; margin-top: 5px; }</style>", unsafe_allow_html=True)
st.markdown("<style>div[data-testid='stPopover'] > button:hover { background: rgba(52, 211, 153, 0.25) !important; border-color: #34D399 !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.pairwise-card { background: linear-gradient(135deg, #1E293B, #0F172A); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 12px 14px; margin-top: 4px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.pairwise-label-set { display: block; text-align: left; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payer-info { font-size: 14px; font-weight: 800; color: #F1F5F9; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payer-sub { font-size: 11px; font-weight: 600; color: #64748B; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payout-pill { background: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid #10B981; padding: 4px 10px; border-radius: 8px; font-size: 15px; font-weight: 900; }</style>", unsafe_allow_html=True)
st.markdown("<style>.whatsapp-box { background: #151F32; border-radius: 10px; padding: 12px; border-left: 3px solid #10B981; font-family: monospace; font-size: 12px; color: #E2E8F0; width: 100%; margin-top: 5px; margin-bottom: 12px; }</style>", unsafe_allow_html=True)

st.markdown("<style>div.stLinkButton > a { width: 100% !important; background: #10B981 !important; color: white !important; border-radius: 10px !important; font-weight: 800 !important; padding: 12px !important; text-align: center !important; text-decoration: none !important; border: none !important; display: block !important; margin-bottom: 15px; }</style>", unsafe_allow_html=True)
st.markdown("<style>div.stLinkButton > a:hover { background: #059669 !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stTabs [data-baseweb='tab-list'] { gap: 8px; margin-bottom: 10px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stTabs [data-baseweb='tab'] { padding: 8px 16px !important; font-size: 13px !important; font-weight: 700 !important; }</style>", unsafe_allow_html=True)

st.markdown('<p class="main-title">💰 MG Settlement Desk</p>', unsafe_allow_html=True)

# --- FIXED: COMPACT BASE FETCH LOGIC ---
def parse_repo_csv(target_url):
    try:
        res = requests.get(target_url)
        if res.status_code == 200:
            raw_b64 = res.json()["content"]
            txt = base64.b64decode(raw_b64).decode("utf-8")
            return pd.read_csv(io.StringIO(txt))
    except:
        pass
    return pd.DataFrame()

# --- CORE PARAMETERS ---
all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]
eco_coefficients = {
    "Manish": 0.18,
    "Abhishek": 0.14,
    "Dk": 0.09,
    "Ajay": 0.09,
    "Ankit": 0.09
}

REPO = st.secrets.get("GITHUB_REPO", "").strip()

URL_PREFIX = "https://api.github.com/repos/"
TRIP_URL = URL_PREFIX + REPO + "/contents/carpool_logs.csv"
EXPENSE_URL = URL_PREFIX + REPO + "/contents/carpool_expenses.csv"

df_trips_raw = pd.DataFrame()
df_expenses_raw = pd.DataFrame()

# --- REMOTE DATA FETCH ---
if REPO:
    cb = "?cb=" + str(random.randint(1, 1000000))
    df_trips_raw = parse_repo_csv(TRIP_URL + cb)
    df_expenses_raw = parse_repo_csv(EXPENSE_URL + cb)

df_trips = df_trips_raw.copy()
df_expenses = df_expenses_raw.copy()

if not df_trips.empty:
    df_trips["Date"] = pd.to_datetime(df_trips["Date"], errors='coerce')
if not df_expenses.empty:
    df_expenses["Date"] = pd.to_datetime(df_expenses["Date"], errors='coerce')

# --- TIMELINE CONTROLS ---
st.markdown('<p class="section-title">📅 Settlement Week</p>', unsafe_allow_html=True)
u_now = datetime.datetime.utcnow()
ist = u_now + datetime.timedelta(hours=5, minutes=30)
tday = ist.date()

wday = tday.weekday()
td_mon = datetime.timedelta(days=wday)
m_day = tday - td_mon

td_fri = datetime.timedelta(days=4)
f_day = m_day + td_fri

m_str = m_day.strftime('%d %b')
f_str = f_day.strftime('%d %b %Y')
current_week_str = f"Current Week ({m_str} - {f_str})"
past_week_str = "Week 21 (18 May - 22 May 2026)"

selected_window = st.selectbox(
    "Choose Billing Week Window:",
    [current_week_str, past_week_str, "All Time Logs Cumulative"],
    label_visibility="collapsed"
)

if selected_window == current_week_str:
    start_w = pd.to_datetime(m_day)
    td_end = datetime.timedelta(days=2)
    end_w = pd.to_datetime(f_day) + td_end
elif selected_window == past_week_str:
    start_w = pd.to_datetime("2026-05-18")
    end_w = pd.to_datetime("2026-05-24")

if selected_window in [current_week_str, past_week_str]:
    if not df_trips.empty:
        df_trips = df_trips[(df_trips["Date"] >= start_w) & (df_trips["Date"] <= end_w)]
    if not df_expenses.empty:
        df_expenses = df_expenses[(df_expenses["Date"] >= start_w) & (df_expenses["Date"] <= end_w)]

# --- CALCULATION ENGINE ---
pairwise_matrix = {payer: {payee: 0.0 for payee in all_commuters} for payer in all_commuters}
driver_counts = {n: 0 for n in all_commuters}
passenger_counts = {n: 0 for n in all_commuters}
total_trips_logged = 0
total_carbon_offset_kg = 0.0

if not df_trips.empty:
    total_trips_logged = len(df_trips)
    for _, row in df_trips.iterrows():
        driver = str(row.get("Driver", "")).strip().title()
        f_pass = str(row.get("Full Day Passengers", ""))
        h_pass = str(row.get("Half Day Passengers", ""))
        
        full_list = [
            p.strip().title() 
            for p in f_pass.split(",") 
            if p.strip() and p.strip().lower() != 'none'
        ]
        half_list = [
            p.strip().title() 
            for p in h_pass.split(",") 
            if p.strip() and p.strip().lower() != 'none'
        ]
        
        if driver in driver_counts:
            driver_counts[driver] += 1
            
        for p in full_list:
            if p in passenger_counts:
                passenger_counts[p] += 1
            if p in all_commuters and driver in all_commuters and p != driver:
                pairwise_matrix[p][driver] += 300.0
            total_carbon_offset_kg += (130.0 * eco_coefficients.get(p, 0.09))
            
        for p in half_list:
            if p in passenger_counts:
                passenger_counts[p] += 1
            if p in all_commuters and driver in all_commuters and p != driver:
                pairwise_matrix[p][driver] += 150.0
            total_carbon_offset_kg += (130.0 * eco_coefficients.get(p, 0.09) * 0.5)

if not df_expenses.empty:
    for _, row in df_expenses.iterrows():
        payer = str(row.get("Paid By", "")).strip().title()
        shared_field = str(row.get("Shared By", ""))
        consumer_list = [p.strip().title() for p in shared_field.split(",") if p.strip()]
        
        try:
            total_amount = float(row.get("Total Amount", row.get("Total amount", 0.0)))
        except:
            total_amount = 0.0
        
        if total_amount > 0 and len(consumer_list) > 0:
            per_person_cost = round(total_amount / len(consumer_list), 2)
            for p in consumer_list:
                if p in all_commuters and payer in all_commuters and p != payer:
                    pairwise_matrix[p][payer] += per_person_cost

# --- BALANCES DIRECT NETTING ---
final_settlements = []
processed_pairs = set()

for p1 in all_commuters:
    for p2 in all_commuters:
        if p1 != p2 and (p1, p2) not in processed_pairs and (p2, p1) not in processed_pairs:
            processed_pairs.add((p1, p2))
            p1_owes = pairwise_matrix[p1][p2]
            p2_owes = pairwise_matrix[p2][p1]
            
            if p1_owes > p2_owes:
                diff = p1_owes - p2_owes
                if diff > 0.01:
                    final_settlements.append((p1, p2, round(diff, 2)))
            elif p2_owes > p1_owes:
                diff = p2_owes - p1_owes
                if diff > 0.01:
                    final_settlements.append((p2, p1, round(diff, 2)))

# --- SCREEN DISPLAY RENDERING ---
st.markdown('<p class="section-title">⚡ Weekly Stats</p>', unsafe_allow_html=True)
top_driver = max(driver_counts, key=driver_counts.get) if total_trips_logged > 0 else "None"
top_passenger = max(passenger_counts, key=passenger_counts.get) if total_trips_logged > 0 else "None"

scorecards_html = f"""
<div class="scorecard-row">
    <div class="scorecard-box">
        <div class="scorecard-label">👑 King of Wheel</div>
        <div class="scorecard-val">{top_driver} ({driver_counts.get(top_driver, 0)} Days)</div>
    </div>
    <div class="scorecard-box">
        <div class="scorecard-label">🎒 Top Passenger</div>
        <div class="scorecard-val">{top_passenger} ({passenger_counts.get(top_passenger, 0)} Rides)</div>
    </div>
</div>
"""
st.markdown(scorecards_html, unsafe_allow_html=True)

tab_payout, tab_raw = st.tabs(["💵 Payouts", "📋 History"])

with tab_payout:
    st.markdown("### 💎 Direct Pairwise Settlements")
    whatsapp_lines = ["*🚗 Carpool Settlement Summary*", "-------------------------------------"]
    
    if not final_settlements:
        st.info("Balances are fully zeroed out!")
    else:
        final_settlements.sort(key=lambda x: x[2], reverse=True)
        for deb, cred, amt in final_settlements:
            card_html = f"""
            <div class="pairwise-card">
                <div class="pairwise-label-set">
                    <div class="payer-info">👉 {deb}</div>
                    <div class="payer-sub">Pays directly to <b>{cred}</b></div>
                </div>
                <div class="payout-pill">₹{amt:,.0f}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            whatsapp_lines.append(f"👉 *{deb}* pays *{cred}*:  *₹{amt:.0f}*")
            
    whatsapp_lines.extend([
        "-------------------------------------",
        "💡 _Calculated via strict per-ride passenger-driver isolation._"
    ])
    whatsapp_text_raw = "\n".join(whatsapp_lines)

    st.write("**🟢 Output Code**")
    box_html = f'<div class="whatsapp-box">{whatsapp_text_raw.replace("\n", "<br>")}</div>'
    st.markdown(box_html, unsafe_allow_html=True)
    st.write("")
    
    msg_url_encoded = urllib.parse.quote(whatsapp_text_raw)
    st.link_button("💬 SHARE DIRECT TO WHATSAPP", f"https://api.whatsapp.com/send?text={msg_url_encoded}")

    st.markdown('<p class="section-title">🌱 Sustainability Performance</p>', unsafe_allow_html=True)
    tree_days_saved = int(total_carbon_offset_kg / 0.06)
    
    eco_card_html = f"""
    <div class="eco-flex-card">
        <div class="eco-flex-title">🌱 MG Eco Impact Profile</div>
        <div class="eco-metric-num">{total_carbon_offset_kg:,.1f} <span class="eco-metric-unit">kg CO₂ Avoided</span></div>
        <div class="eco-sub-text">Equivalent to saving <b>{tree_days_saved:,} Tree-Days</b> of carbon absorption!</div>
    </div>
    """
    st.markdown(eco_card_html, unsafe_allow_html=True)
    
    with st.popover("📋 View Calculation Basis"):
        st.write("**Methodology:** 130 KM baseline per ride tracker.")
        st.write("- **Manish:** BS4 Diesel Engine $\\rightarrow$ `0.18 kg/KM`")
        st.write("- **Abhishek:** BS6 Diesel Engine $\\rightarrow$ `0.14 kg/KM`")
        st.write("- **Others (Dk, Ajay, Ankit):** CNG Configuration $\\rightarrow$ `0.09 kg/KM`")

with tab_raw:
    st.markdown('<p class="section-title">📊 Historical Ledger</p>', unsafe_allow_html=True)
    with st.expander("🚗 View Daily Trip Logs", expanded=True):
        if not df_trips.empty:
            df_trips_display = df_trips.copy()
            df_trips_display["Date"] = df_trips_display["Date"].dt.strftime('%Y-%m-%d')
            st.dataframe(df_trips_display.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No active ride logs captured inside this window timeline.")
            
    with st.expander("💰 View Shared Expense Bills", expanded=False):
        if not df_expenses.empty:
            df_expenses_display = df_expenses.copy()
            df_expenses_display["Date"] = df_expenses_display["Date"].dt.strftime('%Y-%m-%d')
            st.dataframe(df_expenses_display.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No
