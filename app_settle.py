import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random
import urllib.parse

# Pure native config
st.set_page_config(
    page_title="MG",
    layout="centered"
)

st.title("💰 MG Settlement Desk")

# --- DATA REPO PARSER ---
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

# --- NAMES CONFIG ---
names = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]
eco_co = {
    "Manish": 0.18,
    "Abhishek": 0.14,
    "Dk": 0.09,
    "Ajay": 0.09,
    "Ankit": 0.09
}

REPO = st.secrets.get("GITHUB_REPO", "").strip()

PFX = "https://api.github.com/repos/"
TRIP_URL = PFX + REPO + "/contents/carpool_logs.csv"
EXPENSE_URL = PFX + REPO + "/contents/carpool_expenses.csv"

df_t_raw = pd.DataFrame()
df_e_raw = pd.DataFrame()

if REPO:
    cb = "?cb=" + str(random.randint(1, 100000))
    df_t_raw = parse_repo_csv(TRIP_URL + cb)
    df_e_raw = parse_repo_csv(EXPENSE_URL + cb)

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

# --- TIMELINE CONTROLS ---
st.subheader("📅 Settlement Week")
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
        # FIXED: Corrected start_w reference typo to st_w
        df_e = df_e[(df_e["Date"] >= st_w) & (df_e["Date"] <= en_w)]

# --- ENGINE ---
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

# --- NETTING ---
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

# --- DISPLAY ---
st.subheader("⚡ Weekly Stats")
top_d = max(d_cnt, key=d_cnt.get) if t_trips > 0 else "None"
top_p = max(p_cnt, key=p_cnt.get) if t_trips > 0 else "None"

c1, c2 = st.columns(2)
with c1:
    st.metric("👑 King of Wheel", f"{top_d} ({d_cnt.get(top_d,0)} Days)")
with c2:
    st.metric("🎒 Top Passenger", f"{top_p} ({p_cnt.get(top_p,0)} Rides)")

tab_p, tab_r = st.tabs(["💵 Payouts", "📋 History"])

with tab_p:
    st.subheader("💎 Pairwise Settlements")
    wa_lines = ["*🚗 Carpool Settlement*", "-----------------------"]
    
    if not settles:
        st.info("Balances zeroed out!")
    else:
        settles.sort(key=lambda x: x[2], reverse=True)
        for deb, cred, amt in settles:
            st.warning(f"👉 {deb} pays {cred} -> ₹{amt:,.0f}")
            wa_lines.append(f"👉 *{deb}* pays *{cred}*: *₹{amt:.0f}*")
            
    wa_lines.extend(["-----------------------", "💡 _Calculated via Engine Isolation._"])
    wa_text = "\n".join(wa_lines)

    st.write("**🟢 Output Code**")
    st.code(wa_text, language="markdown")
    st.write("")
    
    enc_msg = urllib.parse.quote(wa_text)
    st.link_button("💬 SHARE TO WHATSAPP", f"https://api.whatsapp.com/send?text={enc_msg}")

    st.subheader("🌱 Sustainability Profile")
    t_days = int(co2_kg / 0.06)
    st.metric("CO₂ Avoided", f"{co2_kg:,.1f} kg", f"{t_days:,} Tree-Days Saved")
    
    with st.popover("📋 View Calculation Basis"):
        st.write("130 KM baseline engine calculation.")
        st.write("- Manish: `0.18 kg/KM`")
        st.write("- Abhishek: `0.14 kg/KM`")
        st.write("- Others: `0.09 kg/KM`")

with tab_r:
    st.subheader("📊 Historical Ledger")
    with st.expander("🚗 Daily Trip Logs", expanded=True):
        if not df_t.empty:
            df_disp = df_t.copy()
            df_disp["Date"] = df_disp["Date"].dt.strftime('%Y-%m-%d')
            st.dataframe(df_disp.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No logs found.")
            
    with st.expander("💰 View Shared Expense Bills", expanded=False):
        if not df_e.empty:
            df_edisp = df_e.copy()
            df_edisp["Date"] = df_edisp["Date"].dt.strftime('%Y-%m-%d')
            st.dataframe(df_edisp.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No bills found.")
