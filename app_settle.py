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
st.markdown(
    "<style>"
    "[data-testid='stAppViewContainer']"
    " { background-color: "
    "#0F172A !important; }"
    "</style>",
    unsafe_allow_html=True
)
st.markdown(
    "<style>"
    ".block-container {"
    " background: "
    "rgba(30,41,59,0.5) "
    "!important; padding: "
    "20px !important; "
    "border-radius: "
    "16px !important; "
    "border: 1px solid "
    "rgba(255,255,255,0.08) "
    "!important; "
    "margin-top: 10px "
    "!important; }"
    "</style>",
    unsafe_allow_html=True
)
st.markdown(
    "<style>"
    ".main-title {"
    " font-size: 24px "
    "!important; "
    "font-weight: 900; "
    "color: #FFFFFF "
    "!important; "
    "text-align: center; }"
    "</style>",
    unsafe_allow_html=True
)
st.markdown(
    "<style>"
    ".scorecard-row {"
    " display: flex; "
    "gap: 10px; "
    "width: 100%; }"
    ".scorecard-box {"
    " flex: 1; "
    "background: "
    "rgba(15,23,42,0.6); "
    "border: 1px solid "
    "rgba(255,255,255,0.05); "
    "border-radius: 10px; "
    "padding: 12px; "
    "text-align: center; }"
    ".scorecard-label {"
    " font-size: 11px; "
    "font-weight: 800; "
    "color: #64748B; "
    "text-transform: "
    "uppercase; }"
    ".scorecard-val {"
    " font-size: 14px; "
    "font-weight: 800; "
    "color: #F1F5F9; }"
    "</style>",
    unsafe_allow_html=True
)
st.markdown(
    "<style>"
    ".eco-flex-card {"
    " background: "
    "linear-gradient"
    "(135deg,#064E3B,"
    "#022C22); "
    "border: 1px solid "
    "rgba(16,185,129,0.2); "
    "border-radius: 14px; "
    "padding: 16px; "
    "width: 100%; }"
    ".eco-flex-title {"
    " font-size: 12px "
    "!important; "
    "font-weight: 800; "
    "color: #34D399 "
    "!important; "
    "text-transform: "
    "uppercase; }"
    ".eco-metric-num {"
    " font-size: 26px "
    "!important; "
    "font-weight: 900; "
    "color: #FFFFFF; }"
    ".eco-sub-text {"
    " font-size: 11px "
    "!important; "
    "color: #D1FAE5; "
    "opacity: 0.85; }"
    "</style>",
    unsafe_allow_html=True
)
st.markdown(
    "<style>"
    ".pairwise-card {"
    " background: "
    "linear-gradient"
    "(135deg,#1E293B,"
    "#0F172A); "
    "border: 1px solid "
    "rgba(255,255,255,0.06); "
    "border-radius: 12px; "
    "padding: 12px; "
    "display: flex; "
    "justify-content: "
    "space-between; "
    "align-items: center; "
    "width: 100%; }"
    ".payer-info {"
    " font-size: 14px; "
    "font-weight: 800; "
    "color: #F1F5F9; }"
    ".payout-pill {"
    " background: "
    "rgba(16,185,129,0.12); "
    "color: #10B981; "
    "border: 1px solid "
    "#10B981; "
    "padding: 4px 10px; "
    "border-radius: 8px; "
    "font-size: 14px; "
    "font-weight: 900; }"
    ".whatsapp-box {"
    " background: #151F32; "
    "border-radius: 10px; "
    "padding: 12px; "
    "border-left: 3px solid "
    "#10B981; "
    "font-family: monospace; "
    "color: #E2E8F0; }"
    "</style>",
    unsafe_allow_html=True
)
st.markdown(
    "<style>"
    "div.stLinkButton > a {"
    " width: 100% "
    "!important; "
    "background: #10B981 "
    "!important; "
    "color: white "
    "!important; "
    "border-radius: 10px "
    "!important; "
    "font-weight: 800 "
    "!important; "
    "padding: 12px "
    "!important; "
    "text-align: center; "
    "display: block "
    "!important; }"
    "</style>",
    unsafe_allow_html=True
)

st.markdown(
    '<p class="main-title">'
    '💰 MG Settlement Desk'
    '</p>',
    unsafe_allow_html=True
)

# --- REPO DATA EXTRACTOR ---
def parse_repo_csv(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            b64 = res.json()["content"]
            raw = base64.b64decode(
                b64
            )
            txt = raw.decode("utf-8")
            io_txt = io.StringIO(txt)
            return pd.read_csv(io_txt)
    except:
        pass
    return pd.DataFrame()

# --- CONFIG MATRIX ---
names = [
    "Manish",
    "Abhishek",
    "Dk",
    "Ajay",
    "Ankit"
]
eco_co = {
    "Manish": 0.18,
    "Abhishek": 0.14,
    "Dk": 0.09,
    "Ajay": 0.09,
    "Ankit": 0.09
}

r_sec = st.secrets
REPO = r_sec.get("GITHUB_REPO","")
REPO = REPO.strip()

PFX = "https://api.github.com/repos/"
TRIP_URL = PFX + REPO + "/contents/carpool_logs.csv"
EXP_URL = PFX + REPO + "/contents/carpool_expenses.csv"

df_t_raw = pd.DataFrame()
df_e_raw = pd.DataFrame()

if REPO:
    cb = "?cb=" + str(
        random.randint(1,100000)
    )
    df_t_raw = parse_repo_csv(
        TRIP_URL + cb
    )
    df_e_raw = parse_repo_csv(
        EXP_URL + cb
    )

df_t = df_t_raw.copy()
df_e = df_e_raw.copy()

if not df_t.empty:
    df_t["Date"] = pd.to_datetime(
        df_t["Date"],
        errors='coerce'
    )
if not df_e.empty:
    df_e["Date"] = pd.to_datetime(
        df_e["Date"],
        errors='coerce'
    )

# --- TIMELINE SETUP ---
st.write("**📅 Settlement Week**")
u_now = datetime.datetime.utcnow()
td_add = datetime.timedelta(
    hours=5,
    minutes=30
)
ist = u_now + td_add
tday = ist.date()

wday = tday.weekday()
td_mon = datetime.timedelta(
    days=wday
)
m_day = tday - td_mon

td_fri = datetime.timedelta(
    days=4
)
f_day = m_day + td_fri

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
    td_e = datetime.timedelta(days=2)
    en_w = pd.to_datetime(f_day)
    en_w = en_w + td_e
elif w_sel == p_wk:
    st_w = pd.to_datetime("2026-05-18")
    en_w = pd.to_datetime("2026-05-24")

if w_sel in [c_wk, p_wk]:
    if not df_t.empty:
        f_bit = df_t["Date"] >= st_w
        e_bit = df_t["Date"] <= en_w
        df_t = df_t[f_bit & e_bit]
    if not df_e.empty:
        f_bit = df_e["Date"] >= st_w
        e_bit = df_e["Date"] <= en_w
        df_e = df_e[f_bit & e_bit]

# --- RIDE PROCESSING LOOP ---
mat = {
    p1: {p2: 0.0 for p2 in names} 
    for p1 in names
}
d_cnt = {n: 0 for n in names}
p_cnt = {n: 0 for n in names}
t_trips = 0
co2_kg = 0.0

if not df_t.empty:
    t_trips = len(df_t)
    for _, row in df_t.iterrows():
        drv = str(row.get("Driver",""))
        drv = drv.strip().title()
        f_s = str(row.get("Full Day Passengers",""))
        h_s = str(row.get("Half Day Passengers",""))
        
        f_lst = [
            p.strip().title() 
            for p in f_s.split(",") 
            if p.strip() and 
            p.strip().lower() != 'none'
        ]
        h_lst = [
            p.strip().title() 
            for p in h_s.split(",") 
            if p.strip() and 
            p.strip().lower() != 'none'
        ]
        
        if drv in d_cnt:
            d_cnt[drv] += 1
            
        for p in f_lst:
            if p in p_cnt:
                p_cnt[p] += 1
            if p in names and drv in names and p != drv:
                mat[p][drv] += 300.0
            co2_kg += (
                130.0 * eco_co.get(p, 0.09)
            )
            
        for p in h_lst:
            if p in p_cnt:
                p_cnt[p] += 1
            if p in names and drv in names and p != drv:
                mat[p][drv] += 150.0
