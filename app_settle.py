import streamlit as st
import pandas as pd
import requests
import base64
import io
import random
import datetime
import urllib.parse

st.set_page_config(page_title="MG Settlement", page_icon="📊", layout="centered")

# Visual Engine: Ultra-Lean Cyber-Dark Theme with Sustainability Canvas Styling
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { 
        background-color: #0F172A !important; 
        overflow-y: auto !important; 
    }
    .block-container {
        background: rgba(30, 41, 59, 0.5) !important;
        padding: 15px !important; 
        border-radius: 16px !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; 
        margin-top: 35px !important;
        margin-bottom: 30px !important;
    }
    .main-title { font-size: 22px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 2px; text-align: center; }
    .section-title { font-size: 15px !important; font-weight: 800; color: #94A3B8 !important; margin-top: 12px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Compact Scorecards */
    .scorecard-row { display: flex; gap: 8px; margin-bottom: 5px; }
    .scorecard-box {
        flex: 1; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px; padding: 10px; text-align: center;
    }
    .scorecard-label { font-size: 10px; font-weight: 800; color: #64748B; text-transform: uppercase; }
    .scorecard-val { font-size: 14px; font-weight: 800; color: #F1F5F9; margin-top: 2px; }
    
    /* Sustainability Eco-Impact Profile Box */
    .eco-flex-card {
        background: linear-gradient(135deg, #064E3B, #022C22);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 14px;
        padding: 16px;
        margin-top: 14px;
        margin-bottom: 10px;
        box-shadow: 0px 8px 25px rgba(4, 120, 87, 0.15);
    }
    .eco-flex-title {
        font-family: sans-serif;
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #34D399 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .eco-metric-num {
        font-size: 28px !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        line-height: 1;
    }
    .eco-metric-unit {
        font-size: 14px !important;
        color: #A7F3D0 !important;
        font-weight: 600;
    }
    .eco-sub-text {
        font-size: 12px !important;
        color: #D1FAE5 !important;
        font-weight: 500;
        margin-top: 4px;
        opacity: 0.85;
    }

    /* Lean Pairwise Cards */
    .pairwise-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px;
        padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
    }
    .payer-info { font-size: 14px; font-weight: 800; color: #F1F5F9; }
    .payer-sub { font-size: 11px; font-weight: 600; color: #64748B; }
    .payout-pill { background: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid #10B981; padding: 4px 10px; border-radius: 8px; font-size: 15px; font-weight: 900; }
    
    /* WhatsApp Box */
    .whatsapp-box { background: #151F32; border-radius: 10px; padding: 10px; border-left: 3px solid #10B981; font-family: monospace; font-size: 11px; color: #E2E8F0; }
    
    /* Compact Link Button */
    .whatsapp-btn {
        display: block; text-align: center; width: 100%; background: #10B981;
        color: white !important; border-radius: 10px; font-weight: 800; padding: 10px; text-decoration: none !important;
        font-size: 14px; box-shadow: 0px 3px 10px rgba(16, 185, 129, 0.2); font-family: sans-serif;
    }
    .whatsapp-btn:hover { background: #059669; text-decoration: none !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 6px 12px !important; font-size: 13px !important; }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="main-title">💰 MG Settlement Desk - <span style="font-size: 10px; font-weight: 400; color:
