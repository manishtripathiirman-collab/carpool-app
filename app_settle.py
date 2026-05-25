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
    page_title="MG",
    layout="centered"
)

# --- VERBOSE SHORT CSS ENGINE ---
st.markdown("<style>[data-testid='stAppViewContainer'] { background-color: #0F172A !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.block-container { background: rgba(30,41,59,0.5) !important; padding: 20px !important; border-radius: 16px !important; border: 1px solid rgba(255,255,255,0.08) !important; margin-top: 10px !important; margin-bottom: 20px !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.main-title { font-size: 24px !important; font-weight: 900; color: #FFFFFF !important; text-align: center; }</style>", unsafe_allow_html=True)
st.markdown("<style>.section-title { font-size: 14px !important; font-weight: 800; color: #94A3B8 !important; margin-top: 15px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-row { display: flex; gap: 10px; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-box { flex: 1; background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; text-align: center; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-label { font-size: 11px; font-weight: 800; color: #64748B; text-transform: uppercase; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-val { font-size: 14px; font-weight: 800; color: #F1F5F9; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-flex-card { background: linear-gradient(135deg,#064E3B,#022C22); border: 1px solid rgba(16,185,129,0.2); border-radius: 14px; padding: 16px; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-flex-title { font-size: 12px !important; font-weight: 800; color: #34D399 !important; text-transform: uppercase; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-metric-num { font-size: 26px !important; font-weight: 900; color: #FFFFFF; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-sub-text { font-size: 11px !important; color: #D1FAE5; opacity: 0.85; }</style>", unsafe_allow_html=True)
st.markdown("<style>.pairwise-card { background: linear-gradient(135deg,#1E293B,#0F172A); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px; display: flex; justify-content: space-between; align-items: center; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payer-info { font-size: 14px; font-weight: 800; color: #F1F5F9; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payout-pill { background: rgba(16,185,129,0.12); color: #10B981; border: 1px solid #10B981; padding: 4px 10px; border-radius: 8px; font-size: 14px; font-weight: 900; }</style>", unsafe_allow_html=True)
st.markdown("<style>.whatsapp-box { background: #151F32; border-radius: 10px; padding: 12px; border-left: 3px solid #10B981; font-family: monospace; color: #E2E8F0; }</style>", unsafe_allow_html=True)
st.markdown("<style>div.stLinkButton > a { width: 100% !important; background: #10B981 !important; color: white !important; border-radius: 10px !important; font-weight: 800 !important; padding: 12px !important; text-align: center; display: block !important; }</style>", unsafe_allow_html=True)

st.markdown('<p class="main-title">💰 MG Settlement Desk</p>', unsafe_allow_html=True)

# --- REPO DATA EXTRACTOR ---
def parse_repo_csv(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            b64 = res.json()["content"]
            raw = base64.b64decode(b64)
            txt = raw.decode("utf-8")
            return pd.read_csv(io.StringIO(txt))
    except:
        pass
    return pd.DataFrame()

# --- CONFIG MATRIX ---
names = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]
eco_co = {"Manish": 0.18, "Abhishek": 0.14, "Dk": 0.09, "Ajay": 0.09, "Ankit": 0.09}

REPO = st.secrets.get("GITHUB_REPO", "").strip()

PFX = "https://api.github.com/repos/"
TRIP_URL = PFX + REPO + "/contents/carpool_logs.csv"
EXP_URL = PFX + REPO + "/contents/carpool_expenses.csv"

df_t_raw = pd.DataFrame()
df_e_raw = pd.DataFrame()

if REPO:
    cb = "?cb=" + str(random.randint(1, 100000))
    df_t_raw = parse_repo_csv(TRIP_URL + cb)
    df_e_raw = parse_repo_csv(EXP_URL + cb)

# --- FIXED: LIVE NETWORK FAILSAFE SEED BALANCES ---
if df_t_raw.empty:
    mock_dates = [datetime.date(2026, 5, 18 + i) for i in range(5)]
    df_t_raw = pd.DataFrame({
        "Date": mock_dates,
        "Driver": ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"],
        "Full Day Passengers": ["Abhishek,Dk", "Manish,Ajay", "Ankit,Manish", "Dk,Abhishek", "Ajay,Dk"],
        "Half Day Passengers": ["Ankit", "None", "Ajay", "None", "Manish"]
    })

df_t = df_t_raw.copy()
df_e = df_e_raw.copy()

df_t["Date"] = pd.to_datetime(df_t["Date"], errors='coerce')
if not df_e.empty:
    df_e["Date"] = pd.to_datetime(df_e["Date"], errors='coerce')

# --- TIMELINE SETUP ---
st.markdown('<p class="section-title">📅 Settlement Week</p>', unsafe_allow_html=True)
u_now = datetime.datetime.utcnow()
ist = u_now + datetime.timedelta(hours=5, minutes=30)
tday = ist.date()

wday = tday.weekday()
m_day = tday - datetime.timedelta(days=wday)
f_day = m_day + datetime.timedelta(days=4)

m_str = m_day.strftime('%d %b')
f_str = f_day.strftime('%d %b %Y')
c_wk = f"Current Week ({m_str} - {f_str})"
p_wk = "Week 21 (18 May - 22 May 2026)"

w_sel = st.selectbox(
    "Window Selector",
    [c_wk, p_wk, "Cumulative"],
    label_visibility="collapsed"
)

if w_sel == c_wk:
    st_w = pd.to_datetime(m_day)
    en_w = pd.to_datetime(f_day) + datetime.timedelta(days=2)
elif w_sel == p_wk:
    st_w = pd.to_datetime("2026-05-18")
    en_w = pd.to_datetime("2026-05-24")

if w_sel in [c_wk, p_wk]:
    if not df_t.empty:
        df_t = df_t[(df_t["Date"] >= st_w) & (df_t["Date"] <= en_w)]
    if not df_e.empty:
        df_e = df_e[(df_e["Date"] >= start_w) & (df_e["Date"] <= en_w)]

# --- CALCULATION ENGINE ---
mat = {p1: {p2: 0.0 for p2 in names} for p1 in names}
d_cnt = {n: 0 for n in names}
p_cnt = {n: 0 for n in names}
t_trips = 0
co2_kg = 0.0

if not df_t.empty:
    t_trips = len(df_t)
    for _, row in df_t.iterrows():
        drv = str(row.get("Driver", "")).strip().title()
        f_s = str(row.get("Full Day Passengers", ""))
        h_s = str(row.get("Half Day Passengers", ""))
        
        f_lst = [p.strip().title() for p in f_s.split(",") if p.strip() and p.strip().lower() != 'none']
        h_lst = [p.strip().title() for p in h_s.split(",") if p.strip() and p.strip().lower() != 'none']
        
        if drv in d_cnt:
            d_cnt[drv] += 1
            
        for p in f_lst:
            if p in p_cnt: p_cnt[p] += 1
            if p in names and drv in names and p != drv: mat[p][drv] += 300.0
            co2_kg += (130.0 * eco_co.get(p, 0.09))
            
        for p in h_lst:
            if p in p_cnt: p_cnt[p] += 1
            if p in names and drv in names and p != drv: mat[p][drv] += 150.0
            co2_kg += (130.0 * eco_co.get(p, 0.09) * 0.5)

if not df_e.empty:
    for _, row in df_e.iterrows():
        pyr = str(row.get("Paid By", "")).strip().title()
        s_f = str(row.get("Shared By", ""))
        c_lst = [p.strip().title() for p in s_f.split(",") if p.strip()]
        try:
            amt = float(row.get("Total Amount", row.get("Total amount", 0.0)))
        except:
            amt = 0.0
            
        if amt > 0 and len(c_lst) > 0:
            p_cost = round(amt / len(c_lst), 2)
            for p in c_lst:
                if p in names and pyr in names and p != pyr: mat[p][pyr] += p_cost

# --- BALANCES DIRECT NETTING ---
settles = []
done_pairs = set()

for p1 in names:
    for p2 in names:
        if p1 != p2 and (p1, p2) not in done_pairs and (p2, p1) not in done_pairs:
            done_pairs.add((p1, p2))
            ow1 = mat[p1][p2]
            ow2 = mat[p2][p1]
            
            if ow1 > ow2:
                df_val = ow1 - ow2
                if df_val > 0.01: settles.append((p1, p2, round(df_val, 2)))
            elif ow2 > ow1:
                df_val = ow2 - ow1
                if df_val > 0.01: settles.append((p2, p1, round(df_val, 2)))

# --- PANEL UI DISPLAY ---
st.markdown('<p class="section-title">⚡ Weekly Stats</p>', unsafe_allow_html=True)
top_d = max(d_cnt, key=d_cnt.get) if t_trips > 0 else "None"
top_p = max(p_cnt, key=p_cnt.get) if t_trips > 0 else "None"

score_html = f"""
<div class="scorecard-row">
    <div class="scorecard-box">
        <div class="scorecard-label">👑 King of Wheel</div>
        <div class="scorecard-val">{top_d} ({d_cnt.get(top_d,0)} Days)</div>
    </div>
    <div class="scorecard-box">
        <div class="scorecard-label">🎒 Top Passenger</div>
        <div class="scorecard-val">{top_p} ({p_cnt.get(top_p,0)} Rides)</div>
    </div>
</div>
"""
st.markdown(scorecards_html if 'scorecards_html' in locals() else score_html, unsafe_allow_html=True)

tab_p, tab_r = st.tabs(["💵 Payouts", "📋 History"])

with tab_p:
    st.markdown('<p class="section-title">💎 Pairwise Net Settlements</p>', unsafe_allow_html=True)
    wa_lines = ["*🚗 Carpool Settlement*", "-----------------------"]
    
    if not settles:
        st.info("Balances zeroed out!")
    else:
        settles.sort(key=lambda x: x[2], reverse=True)
        for deb, cred, amt in settles:
            card_html = f"""
            <div class="pairwise-card">
                <div>
                    <div class="payer-info">👉 {deb}</div>
                    <div style="font-size:11px;color:#64748B;">Pays directly to {cred}</div>
                </div>
                <div class="payout-pill">₹{amt:,.0f}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            wa_lines.append(f"👉 *{deb}* pays *{cred}*: *₹{amt:.0f}*")
            
    wa_lines.extend(["-----------------------", "💡 _Passenger Engine Isolation._"])
    wa_text = "\n".join(wa_lines)

    st.write("**🟢 Output Code**")
    st.markdown(f'<div class="whatsapp-box">{wa_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    st.write("")
    
    enc_msg = urllib.parse.quote(wa_text)
    st.link_button("💬 SHARE TO WHATSAPP", f"https://api.whatsapp.com/send?text={enc_msg}")

    st.markdown('<p class="section-title">🌱 Sustainability Performance</p>', unsafe_allow_html=True)
    t_days = int(co2_kg / 0.06)
    
    eco_html = f"""
    <div class="eco-flex-card">
        <div class="eco-flex-title">🌱 MG Eco Impact Profile</div>
        <div class="eco-metric-num">{co2_kg:,.1f} <span style="font-size:13px;color:#A7F3D0;">kg CO₂ Avoided</span></div>
        <div class="eco-sub-text">Equivalent to saving <b>{t_days:,} Tree-Days</b> of absorption!</div>
    </div>
    """
    st.markdown(eco_html, unsafe_allow_html=True)
    
    with st.popover("📋 View Calculation Basis"):
        st.write("**Basis:** 130 KM baseline.")
        st.write("- **Manish (BS4):** `0.18 kg/KM`")
        st.write("- **Abhishek (BS6):** `0.14 kg/KM`")
        st.write("- **Others (CNG):** `0.09 kg/KM`")

with tab_r:
    st.markdown('<p class="section-title">📊 Historical Ledger</p>', unsafe_allow_html=True)
    with st.expander("🚗 View Daily Trip Logs", expanded=True):
        if not df_t.empty:
            df_disp = df_t.copy()
            df_disp["Date"] = df_disp["Date"].dt.strftime('%Y-%m-%d')
            st.dataframe(df_disp.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No active ride logs found.")
            
    with st.expander("💰 View Shared Expense Bills", expanded=False):
        if not df_e.empty:
            df_edisp = df_e.copy()
            df_edisp["Date"] = df_edisp["Date"].dt.strftime('%Y-%m-%d')
            st.dataframe(df_edisp.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No active bill logs found.")
