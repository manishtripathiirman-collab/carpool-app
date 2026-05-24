import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time

st.set_page_config(page_title="MG Logger", page_icon="📝", layout="centered")

# Visual Engine: Enhanced Stacking Layering with Deep Charcoal Input Boxes
st.markdown("""
    <style>
    /* Main Background Engine */
    .stApp {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(244, 63, 94, 0.2) 50%, rgba(15, 23, 42, 0.95) 100%), 
                    url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80') !important;
        background-size: cover !important; 
        background-position: center !important; 
        background-attachment: fixed !important;
    }
    
    /* Central Content Shield */
    .block-container {
        background: rgba(15, 23, 42, 0.88) !important;
        backdrop-filter: blur(16px);
        padding: 25px !important;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.6);
        margin-top: 30px !important;
    }
    
    /* Typography Engine */
    .mobile-title { font-family: sans-serif; font-size: 28px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 20px; }
    label, p, span, h2, h3, h4 { color: #F1F5F9 !important; font-weight: 700 !important; }
    
    /* Input Form Boxes Style Controls */
    div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div, .stSelectbox div { 
        background-color: #1E293B !important; 
        border-radius: 12px !important; 
        border: 1px solid rgba(255, 255, 255, 0.3) !important; 
    }
    
    /* Ensure all text values, labels, and icons inside select fields stay bright white */
    div[data-baseweb="select"] *, div[data-baseweb="base-input"] *, .stDateInput div *, .stSelectbox div * { 
        color: #FFFFFF !important; 
    }
    
    /* Fix the placeholder 'Choose options' text color */
    div[data-baseweb="select"] div div:dfn { color: #94A3B8 !important; }
    
    /* Dropdown Option Selection List Popovers */
    div[role="listbox"] { background-color: #1E293B !important; border: 1px solid rgba(255,255,255,0.3) !important; }
    div[role="listbox"] li { color: #FFFFFF !important; font-weight: 700 !important; }
    div[role="listbox"] li:hover { background-color: #334155 !important; }
    
    /* Multi-select individual passenger tags */
    div[data-baseweb="tag"] { background-color: #334155 !important; border-radius: 6px; }
    div[data-baseweb="tag"] span { color: #FFFFFF !important; }
    
    /* Tab Headers Structural Adjustments */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(30, 41, 59, 0.9) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px 10px 0px 0px; padding: 12px 24px !important; color: #94A3B8 !important; font-weight: 700; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366F1, #4F46E5) !important; color: white !important; border-color: #6366F1 !important; }
    
    /* Button Matrix */
    div.stButton > button { width: 100%; background: linear-gradient(90deg, #6366F1, #EC4899) !important; color: white !important; border-radius: 14px; font-weight: 800; padding: 14px; border: none !important; box-shadow: 0px 4px 15px rgba(236, 72, 153, 0.4); }
    .admin-btn > div.stButton > button { background: linear-gradient(90deg, #EF4444, #DC2626) !important; box-shadow: 0px 4px 12px rgba(239, 68, 68, 0.4); }
    .back-btn > div.stButton > button { background: rgba(51, 65, 85, 0.9) !important; border: 1px solid rgba(255,255,255,0.2) !important; margin-top: 15px; box-shadow: none; }
    .exit-admin-btn > div.stButton > button { background: #0F172A !important; border: 1px solid rgba(255,255,255,0.1) !important; margin-top: 10px; color: #E2E8F0 !important; }
    
    /* Neon Status Badge System */
    .neon-badge { display: inline-block; padding: 6px 14px; font-size: 11px; font-weight: 900; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .badge-driver { background-color: rgba(34, 197, 94, 0.25); color: #4ADE80; border: 1px solid #22C55E; box-shadow: 0 0 12px rgba(34,197,94,0.4); }
    .badge-full { background-color: rgba(56, 189, 248, 0.25); color: #38BDF8; border: 1px solid #0EA5E9; box-shadow: 0 0 12px rgba(56,189,248,0.4); }
    .badge-half { background-color: rgba(251, 191, 36, 0.25); color: #FBBF24; border: 1px solid #D97706; box-shadow: 0 0 12px rgba(251,191,36,0.4); }
    .badge-holiday { background-color: rgba(168, 85, 247, 0.25); color: #C084FC; border: 1px solid #9333EA; }
    
    .lock-banner { background-color: #0F172A; border: 2px solid #EF44
