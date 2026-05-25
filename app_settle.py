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
    try:
        cb_val = str(random.randint(1, 1000000))
        
        r = requests.get(TRIP_URL + "?cb=" + cb_val)
        if r.status_code == 200:
            content_decoded = base64.b64decode(r.json()["content"]).decode("utf-8")
            df_trips_raw = pd.read_csv(io.StringIO(content_decoded))
        
        r_e = requests.get(EXPENSE_URL + "?cb=" + cb_val)
        if r_e.status_code == 200:
            content_exp_decoded = base64.b64decode(r_e.json()["content"]).decode("utf-8")
