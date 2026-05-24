import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random

st.set_page_config(page_title="MG Logger", page_icon="🚗", layout="centered")

# Visual Engine: Pure Dark Layout with Fixed Header Margin Spacing
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0F172A !important;
    }
    .block-container {
        background: rgba(30, 41, 59, 0.7) !important;
        padding: 25px !important; 
        border-radius: 20px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5) !important; 
        margin-top: 40px !important;
    }
    .mobile-title { font-family: sans-serif; font-size: 24px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 20px; }
    label, p, span, h2, h3, h4 { color: #F1F5F9 !important; font-weight: 700 !important; }
    div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div { 
        background-color: #1E293B !important; border-radius: 10px !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; 
    }
    div[data-baseweb="select"] [data-user-value="true"], .stSelectbox div [data-baseweb="select"] span, div[data-baseweb="base-input"] input { 
        color: #FFFFFF !important; font-weight: 700 !important; 
    }
    div[role="listbox"] { background-color: #1E293B !important; border: 1px solid rgba(255,255,255,0.2) !important; }
    div[role="listbox"] li { color: #FFFFFF !important; font-weight: 700 !important; }
    div[role="listbox"] li:hover { background-color: #334155 !important; }
    div[data-baseweb="tag"] { background-color: #334155 !important; border-radius: 6px; }
    div[data-baseweb="tag"] span { color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 8px 8px 0px 0px; padding: 10px 20px !important; color: #94A3B8 !important; font-weight: 700; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366F1, #4F46E5) !important; color: white !important; border-color: #6366F1 !important; }
    div.stButton > button { width: 100%; background: linear-gradient(90deg, #6366F1, #EC4899) !important; color: white !important; border-radius: 12px; font-weight: 800; padding: 14px; border: none !important; box-shadow: 0px 4px 15px rgba(236, 72, 153, 0.3); }
    .admin-btn > div.stButton > button { background: linear-gradient(90deg, #EF4444, #DC2626) !important; box-shadow: 0px 4px 12px rgba(239, 68, 68, 0.3); }
    .neon-badge { display: inline-block; padding: 6px 14px; font-size: 11px; font-weight: 900; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .badge-driver { background-color: rgba(34, 197, 94, 0.25); color: #4ADE80; border: 1px solid #22C55E; box-shadow: 0 0 12px rgba(34,197,94,0.4); }
    .badge-full { background-color: rgba(56, 189, 248, 0.25); color: #38BDF8; border: 1px solid #0EA5E9; box-shadow: 0 0 12px rgba(56,189,248,0.4); }
    .badge-half { background-color: rgba(251, 191, 36, 0.25); color: #FBBF24; border: 1px solid #D97706; box-shadow: 0 0 12px rgba(251,191,36,0.4); }
    .badge-holiday { background-color: rgba(168, 85, 247, 0.25); color: #C084FC; border: 1px solid #9333EA; }
    .lock-banner { background-color: #0F172A; border: 2px solid #EF4444; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 10px; box-shadow: 0px 0px 20px rgba(239, 68, 68, 0.3); }
    .future-banner { background-color: #0F172A; border: 2px solid #EAB308; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 10px; box-shadow: 0px 0px 20px rgba(234, 179, 8, 0.3); }
    </style>
    """, 
    unsafe_allow_html=True
)

# Regular hyphen-dash with ultra-small lowercase mantri signature
st.markdown('<p class="mobile-title">🌅 MG Carpool Hub - <span style="font-size: 10px; font-weight: 400; color: #64748B; text-transform: lowercase; vertical-align: middle;">mantri</span></p
