import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time

st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

# Visual Engine: Fixed CSS Hierarchy with High Contrast Input Targets
st.markdown("""
    <style>
    /* Background Base Rules */
    .stApp {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%), 
                    url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80') !important;
        background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
    }
    
    /* Central Content Shield */
    .block-container {
        background: rgba(30, 41, 59, 0.7) !important; backdrop-filter: blur(16px);
        padding: 25px !important; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.5); margin-top: 30px !important;
    }
    
    .mobile-title { font-family: sans-serif; font-size: 28px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 20px; }
    label, p, span, h2, h3, h4 { color: #F1F5F9 !important; font-weight: 700 !important; }
    
    /* CLEAN INPUT FORMS: Uses native dark formatting parameters for full text field safety */
    div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div, .stSelectbox div { 
        background-color: rgba(15, 23, 42, 0.9) !important; border-radius: 12px !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; 
    }
    
    /* Targets input value text values exclusively to white while preserving baseline icon rendering layers */
    div[data-baseweb="select"] [data-user-value="true"], 
    .stSelectbox div [data-baseweb="select"] span,
    div[data-baseweb="base-input"] input { 
        color: #FFFFFF !important; font-weight: 700 !important;
    }
    
    div[role="listbox"] { background-color: #1E293B !important; border: 1px solid rgba(255,255,255,0.3) !important; }
    div[role="listbox"] li { color: #FFFFFF !important; font-weight: 700 !important; }
    div[role="listbox"] li:hover { background-color: #334155 !important; }
    div[data-baseweb="tag"] { background-color: #334155 !important; border-radius: 6px; }
    div[data-baseweb="tag"] span { color: #FFFFFF !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(30, 41, 59, 0.9) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px 10px 0px 0px; padding: 12px 24px !important; color: #94A3B8 !important; font-weight: 700; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366F1, #4F46E5) !important; color: white !important; border-color: #6366F1 !important; }
    
    div.stButton > button { width: 100%; background: linear-gradient(90deg, #6366F1, #EC4899) !important; color: white !important; border-radius: 14px; font-weight: 800; padding: 14px; border: none !important; box-shadow: 0px 4px 15px rgba(236, 72, 153, 0.4); }
    .admin-btn > div.stButton > button { background: linear-gradient(90deg, #EF4444, #DC2626) !important; box-shadow: 0px 4px 12px rgba(239, 68, 68, 0.4); }
    
    .neon-badge { display: inline-block; padding: 6px 14px; font-size: 11px; font-weight: 900; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .badge-driver { background-color: rgba(34, 197, 94, 0.25); color: #4ADE80; border: 1px solid #22C55E; box-shadow: 0 0 12px rgba(34,197,94,0.4); }
    .badge-full { background-color: rgba(56, 189, 248, 0.25); color: #38BDF8; border: 1px solid #0EA5E9; box-shadow: 0 0 12px rgba(56,189,248,0.4); }
    .badge-half { background-color: rgba(251, 191, 36, 0.25); color: #FBBF24; border: 1px solid #D97706; box-shadow: 0 0 12px rgba(251,191,36,0.4); }
    .badge-holiday { background-color: rgba(168, 85, 247, 0.25); color: #C084FC; border: 1px solid #9333EA; }
    .lock-banner { background-color: #0F172A; border: 2px solid #EF4444; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
    .future-banner { background-color: #0F172A; border: 2px solid #EAB308; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(234, 179, 8, 0.3); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="mobile-title">🌅 MG Carpool Hub</p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

if "holiday_list" not in st.session_state: st.session_state.holiday_list = []
if "just_saved" not in st.session_state: st.session_state.just_saved = False
if "saved_message" not in st.session_state: st.session_state.saved_message = ""
if "last_processed_date" not in st.session_state: st.session_state.last_processed_date = None
if "disable_lock" not in st.session_state: st.session_state.disable_lock = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False

utc_now = datetime.datetime.utcnow()
ist_now = utc_now
