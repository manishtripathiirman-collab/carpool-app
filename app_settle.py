import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random
import urllib.parse

st.set_page_config(page_title="MG Settlement", page_icon="📊", layout="centered")

# Visual Engine: Compressed Single Lines to Prevent Truncation Crashes Permanent Fix
st.markdown("<style>[data-testid='stAppViewContainer'] { background-color: #0F172A !important; overflow-y: auto !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.block-container { background: rgba(30, 41, 59, 0.5) !important; padding: 15px !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; margin-top: 35px !important; margin-bottom: 30px !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.main-title { font-size: 22px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 2px; text-align: center; }</style>", unsafe_allow_html=True)
st.markdown("<style>.section-title { font-size: 15px !important; font-weight: 800; color: #94A3B8 !important; margin-top: 12px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-row { display: flex; gap: 8px; margin-bottom: 5px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-box { flex: 1; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 10px; text-align: center; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-label { font-size: 10px; font-weight: 800; color: #64748B; text-transform: uppercase; }</style>", unsafe_allow_html=True)
st.markdown("<style>.scorecard-val { font-size: 14px; font-weight: 800; color: #F1F5F9; margin-top: 2px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-flex-card { background: linear-gradient(135deg, #064E3B, #022C22); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 14px; padding: 16px; margin-top: 14px; margin-bottom: 10px; box-shadow: 0px 8px 25px rgba(4, 120, 87, 0.15); }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-flex-title { font-size: 13px !important; font-weight: 800 !important; color: #34D399 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-metric-num { font-size: 28px !important; font-weight: 900 !important; color: #FFFFFF !important; line-height: 1; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-metric-unit { font-size: 14px !important; color: #A7F3D0 !important; font-weight: 600; }</style>", unsafe_allow_html=True)
st.markdown("<style>.eco-sub-text { font-size: 12px !important; color: #D1FAE5 !important; font-weight: 500; margin-top: 4px; margin-bottom: 12px; opacity: 0.85; }</style>", unsafe_allow_html=True)
st.markdown("<style>div[data-testid='stPopover'] > button { background: rgba(52, 211, 153, 0.15) !important; color: #34D399 !important; border: 1px solid rgba(52, 211, 153, 0.3) !important; padding: 4px 12px !important; font-size: 11px !important; font-weight: 700 !important; border-radius: 8px !important; text-transform: uppercase !important; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>div[data-testid='stPopover'] > button:hover { background: rgba(52, 211, 153, 0.25) !important; border-color: #34D399 !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.pairwise-card { background: linear-gradient(135deg, #1E293B, #0F172A); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payer-info { font-size: 14px; font-weight: 800; color: #F1F5F9; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payer-sub { font-size: 11px; font-weight: 600; color: #64748B; }</style>", unsafe_allow_html=True)
st.markdown("<style>.payout-pill { background: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid #10B981; padding: 4px 10px; border-radius: 8px; font-size: 15px; font-weight: 900; }</style>", unsafe_allow_html=True)
st.markdown("<style>.whatsapp-box { background: #151F32; border-radius: 10px; padding: 10px; border-left: 3px solid #10B981; font-family: monospace; font-size: 11px; color: #E2E8F0; }</style>", unsafe_allow_html=True)
st.markdown("<style>.whatsapp-btn { display: block; text-align: center; width: 100%; background: #10B981; color: white !important; border-radius: 10px; font-weight: 800; padding: 10px; text-decoration: none !important; font-size: 14px; box-shadow: 0px 3px 10px rgba(16, 185, 129, 0.2); }</style>", unsafe_allow_html=True)
st.markdown("<style>.whatsapp-btn:hover { background: #059669; text-decoration: none !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stTabs [data-baseweb='tab-list'] { gap: 4px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stTabs [data-baseweb='tab'] { padding: 6px 12px !important; font-size: 13px !important; }</style>", unsafe_allow_html=True)

st.markdown('<p class="main-title">💰 MG Settlement Desk</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

TOKEN = st.secrets.get("GITHUB_TOKEN", "").strip()
REPO = st.secrets.get("GITHUB_REPO", "").strip()

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "Cache-Control": "no-cache"}

URL_PREFIX = "https://api.github.com/repos/"
TRIP_URL = URL_PREFIX + REPO + "/contents/carpool_logs.csv"
EXPENSE_URL = URL_PREFIX + REPO + "/contents/carpool_expenses.csv"

df_trips_raw = pd.DataFrame()
df_expenses_raw = pd.DataFrame()

if TOKEN and REPO:
    try:
        cb_val = str(random.randint(1, 1000000))
        t_req_url = TRIP_URL + "?cb=" + cb_val
        e_req_url = EXPENSE_URL + "?cb=" + cb_val
        
        r = requests.get(t_req_url, headers=HEADERS)
        if r.status_code == 200:
            df_trips_raw = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
            
        r_e = requests.get(e_req_url, headers=HEADERS)
        if r_e.status_code == 200:
            df_expenses_raw = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))
    except Exception: pass

df_trips = df_trips_raw.copy()
df_expenses = df_expenses_raw.copy()

if not df_trips.empty: df_trips["Date"] = pd.to_datetime(df_trips["Date"], errors='coerce')
if not df_expenses.empty: df_expenses["Date"] = pd.to_datetime(df_expenses["Date"], errors='coerce')

st.markdown('<p class="section-title">📅 Settlement Week</p>', unsafe_allow_html=True)
