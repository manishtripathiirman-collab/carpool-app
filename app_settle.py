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

# Visual Engine: Ultra-Lean Theme with Fixed Text Target Selectors
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
    
    /* Scorecards Layout */
    .scorecard-row { display: flex; gap: 8px; margin-bottom: 5px; }
    .scorecard-box {
        flex: 1; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px; padding: 10px; text-align: center;
    }
    .scorecard-label { font-size: 10px; font-weight: 800; color: #64748B; text-transform: uppercase; }
    .scorecard-val { font-size: 14px; font-weight: 800; color: #F1F5F9; margin-top: 2px; }
    
    /* Emerald Sustainability Card */
    .eco-flex-card {
        background: linear-gradient(135deg, #064E3B, #022C22);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 14px; padding: 16px; margin-top: 14px; margin-bottom: 10px;
        box-shadow: 0px 8px 25px rgba(4, 120, 87, 0.15);
    }
    .eco-flex-title {
        font-size: 13px !important; font-weight: 800 !important; color: #34D399 !important;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
    }
    .eco-metric-num { font-size: 28px !important; font-weight: 900 !important; color: #FFFFFF !important; line-height: 1; }
    .eco-metric-unit { font-size: 14px !important; color: #A7F3D0 !important; font-weight: 600; }
    .eco-sub-text { font-size: 12px !important; color: #D1FAE5 !important; font-weight: 500; margin-top: 4px; margin-bottom: 12px; opacity: 0.85; }
    
    /* Popover Compact Layout */
    div[data-testid="stPopover"] > button {
        background: rgba(52, 211, 153, 0.15) !important; color: #34D399 !important;
        border: 1px solid rgba(52, 211, 153, 0.3) !important;
        padding: 4px 12px !important; font-size: 11px !important; font-weight: 700 !important;
        border-radius: 8px !important; text-transform: uppercase !important; width: 100%;
    }
    div[data-testid="stPopover"] > button:hover { background: rgba(52, 211, 153, 0.25) !important; border-color: #34D399 !important; }

    /* Pairwise Cards Display */
    .pairwise-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px;
        padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
    }
    .payer-info { font-size: 14px; font-weight: 800; color: #F1F5F9; }
    .payer-sub { font-size: 11px; font-weight: 600; color: #64748B; }
    .payout-pill {
