import streamlit as st
import datetime
import pandas as pd
import requests
import base64
import io
import time
import random

st.set_page_config(page_title="MG Logger", page_icon="🚗", layout="centered")

# Visual Engine: Pure Dark Layout with Label Auto-Scale & Anti-Truncation Engine
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0F172A !important;
        overflow-y: auto !important;
    }
    .block-container {
        background: rgba(30, 41, 59, 0.7) !important;
        padding: 25px !important; 
        border-radius: 20px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5) !important; 
        margin-top: 35px !important;
        margin-bottom: 30px !important;
    }
    .mobile-title { font-family: sans-serif; font-size: 24px !important; font-weight: 900; color: #FFFFFF !important; margin-bottom: 20px; }
    
    label, p, span, h2, h3, h4 { 
        color: #F1F5F9 !important; 
        font-weight: 700 !important;
        white-space: normal !important;
        word-break: break-word !important;
        display: inline-block !important;
    }
    div[data-testid="stWidgetLabel"] {
        white-space: normal !important;
        word-break: break-word !important;
    }
    
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
    
    .giant-lock-banner { 
        background-color: #0F172A; border: 3px solid #EF4444; padding: 40px 20px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0px 0px 30px rgba(239, 68, 68, 0.4); 
    }
    .giant-future-banner { 
        background-color: #0F172A; border: 3px solid #EAB308; padding: 40px 20px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0px 0px 30px rgba(234, 179, 8, 0.4); 
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<p class="mobile-title">🌅 MG Carpool Hub - <span style="font-size: 10px; font-weight: 400; color: #64748B; text-transform: lowercase; vertical-align: middle;">mantri</span></p>', unsafe_allow_html=True)

all_commuters = ["Manish", "Abhishek", "Dk", "Ajay", "Ankit"]

# Time calculations
utc_now = datetime.datetime.utcnow()
ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
today_date_ist = ist_now.date()

# State Engine
if "holiday_list" not in st.session_state: st.session_state.holiday_list = []
if "just_saved" not in st.session_state: st.session_state.just_saved = False
if "just_saved_exp" not in st.session_state: st.session_state.just_saved_exp = False
if "saved_message" not in st.session_state: st.session_state.saved_message = ""
if "last_processed_date" not in st.session_state: st.session_state.last_processed_date = None
if "disable_lock" not in st.session_state: st.session_state.disable_lock = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "reset_trigger" not in st.session_state: st.session_state["reset_trigger"] = 0

TOKEN = st.secrets.get("GITHUB_TOKEN", "").strip()
REPO = st.secrets.get("GITHUB_REPO", "").strip()

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache"
}

TRIP_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_logs.csv"
EXPENSE_URL = f"https://api.github.com/repos/{REPO}/contents/carpool_expenses.csv"

df_existing = pd.DataFrame()
df_exp_existing = pd.DataFrame()

if TOKEN and REPO:
    try:
        r = requests.get(f"{TRIP_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r.status_code == 200:
            df_existing = pd.read_csv(io.StringIO(base64.b64decode(r.json()["content"]).decode("utf-8")))
        
        r_e = requests.get(f"{EXPENSE_URL}?cb={random.randint(1, 1000000)}", headers=HEADERS)
        if r_e.status_code == 200:
            df_exp_existing = pd.read_csv(io.StringIO(base64.b64decode(r_e.json()["content"]).decode("utf-8")))
    except Exception:
        pass

tab_trip, tab_expense = st.tabs(["🚗 Log Commute", "💰 Split Expenses"])

with tab_trip:
    travel_date = st.date_input(
        "Date of Travel", 
        today_date_ist, 
        key=f"trip_date_picker_bound_{st.session_state['reset_trigger']}"
    )

    if st.session_state.last_processed_date != str(travel_date):
        st.session_state.disable_lock = False
        st.session_state.last_processed_date = str(travel_date)

    is_future_date = travel_date > today_date_ist
    
    date_exists = False
    if not df_existing.empty and "Date" in df_existing.columns:
        target_dash = travel_date.strftime("%Y-%m-%d").strip()
        target_slash = travel_date.strftime("%Y/%m/%d").strip()
        df_existing["Cleaned_Date_Str"] = df_existing["Date"].astype(str).str.strip()
        date_exists = (target_dash in df_existing["Cleaned_Date_Str"].values) or (target_slash in df_existing["Cleaned_Date_Str"].values)

    if is_future_date:
        st.markdown(
            """
            <div class='giant-future-banner'>
                <h1 style='font-size:75px;margin:0;'>🔮</h1>
                <h2 style='font-size:38px;color:#EAB308;font-weight:900;margin:15px 0;line-height:1.2;'>Ye kam bhi Loudu ka hi hai</h2>
                <h4 style='font-size:20px;color:#F1F5F9;font-weight:700;margin:0;'>You cannot log entries for future dates.</h4>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("🔙 GO BACK / CHANGE DATE", key="back_future_btn"):
            st.session_state["reset_trigger"] += 1
            st.rerun()

    elif st.session_state.just_saved:
        st.success(st.session_state.saved_message)
        st.session_state.just_saved = False
        time.sleep(1.5)
        st.rerun()

    elif date_exists and not st.session_state.is_admin and not st.session_state.disable_lock:
        st.markdown(
            """
            <div class='giant-lock-banner'>
                <h1 style='font-size:75px;margin:0;'>🛑</h1>
                <h2 style='font-size:38px;color:#EF4444;font-weight:900;margin:15px 0;line-height:1.2;'>Abe Loudu dubara kyun kar raha!</h2>
                <h4 style='font-size:20px;color:#F1F5F9;font-weight:700;margin:0;'>Ab mantri karega Sahi.</h4>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("🔙 GO BACK / CHANGE DATE", key="back_lock_btn"):
            st.session_state["reset_trigger"] += 1
            st.rerun()

    else:
        commuters = [c for c in all_commuters if c not in st.session_state.holiday_list]
        if not commuters: commuters = all_commuters

        driver = st.selectbox("Designated Driver", commuters, key="driver_select_box")
        passenger_options = [c for c in commuters if c != driver]
        full_day = st.multiselect("Full-Day Passengers (₹300)", passenger_options, key="full_select_box")
        half_day = st.multiselect("Half-Day Passengers (₹150)", [p for p in passenger_options if p not in full_day], key="half_select_box")

        if st.button("💾 SAVE TRIP TO LEDGER"):
            full_str = ", ".join([p.strip().title() for p in full_day]) if full_day else "None"
            half_str = ", ".join([p.strip().title() for p in half_day]) if half_day else "None"
            
            new_row = pd.DataFrame([{"Date": str(travel_date), "Driver": driver.strip().title(), "Full Day Passengers": full_str, "Half Day Passengers": half_str}])
            
            if date_exists and st.session_state.is_admin and not df_existing.empty:
                t_dash = travel_date.strftime("%Y-%m-%d").strip()
                t_slash = travel_date.strftime("%Y/%m/%d").strip()
                df_existing["Cleaned_Date_Str"] = df_existing["Date"].astype(str).str.strip()
                df_cleaned_base = df_existing[(df_existing["Cleaned_Date_Str"] != t_dash) & (df_existing["Cleaned_Date_Str"] != t_slash)]
                df_final = pd.concat([df_cleaned_base, new_row], ignore_index=True)
            else:
                df_final = pd.concat([df_existing, new_row], ignore_index=True) if not df_existing.empty else new_row
            
            if "Cleaned_Date_Str" in df_final.columns: df_final = df_final.drop(columns=["Cleaned_Date_Str"])
            
            payload = {"message": f"Update trip logs for {travel_date}", "content": base64.b64encode(df_final.to_csv(index=False).encode("utf-8")).decode("utf-8")}
            
            sha_query_url = f"{TRIP_URL}?cb={random.randint(1, 1000000)}"
            r_sha = requests.get(url=sha_query_url, headers=HEADERS)
            if r_sha.status_code == 200: payload["sha"] = r_sha.json()["sha"]
            
            res_put = requests.put(TRIP_URL, headers=HEADERS, json=payload)
            if res_put.status_code in [200, 201]:
                st.toast(f"🚗 Commute log saved for {travel_date}!", icon="✅")
                st.session_state.just_saved = True
                st.session_state.saved_message = f"🎉 Trip saved cleanly to ledger!"
                st.session_state.disable_lock = True
                st.rerun()
            else:
                st.error(f"🛑 Sync Failure updating ledger file.")

with tab_expense:
    st.markdown("### 💰 Shared Expense Desk")
    
    edit_mode = st.checkbox("✏️ Modify Existing Entry", value=False, key="exp_edit_mode_toggle")
    exp_date = st.date_input("Date of Expense", today_date_ist, key="exp_date_picker")
    is_future_exp_date = exp_date > today_date_ist

    if is_future_exp_date:
        st.markdown(
            """
            <div class='giant-future-banner'>
                <h1 style='font-size:75px;margin:0;'>🔮</h1>
                <h2 style='font-size:38px;color:#EAB308;font-weight:900;margin:15px 0;line-height:1.2;'>Ye kam bhi Loudu ka hi hai</h2>
                <h4 style='font-size:20px;color:#F1F5F9;font-weight:700;margin:0;'>You cannot log expenses for future dates.</h4>
            </div>
            """, 
            unsafe_allow_html=True
        )
    elif st.session_state.just_saved_exp:
        st.success("🎉 Expense bill updated cleanly in database ledger!")
        st.session_state.just_saved_exp = False
        time.sleep(1.5)
        st.rerun()
    else:
        default_payer = all_commuters[0]
        default_amount = 0.0
        default_desc = ""
        default_shares = all_commuters
        expense_exists = False
        
        # Build strict matching strings for tracking dates
        t_dash_e = exp_date.strftime("%Y-%m-%d").strip()
        t_slash_e = exp_date.strftime("%Y/%m/%d").strip()
        
        date_matches = pd.DataFrame()
        if not df_exp_existing.empty and "Date" in df_exp_existing.columns:
            df_exp_existing["Cleaned_Date_Str"] = df_exp_existing["Date"].astype(str).str.strip()
            date_matches = df_exp_existing[(df_exp_existing["Cleaned_Date_Str"] == t_dash_e) | (df_exp_existing["Cleaned_Date_Str"] == t_slash_e)]

        if edit_mode:
            if date_matches.empty:
                st.info("ℹ️ No expenses logged on this date to modify.")
                item_desc = ""
            else:
                desc_list = date_matches["Description"].tolist()
                selected_desc = st.selectbox("Select existing description to modify:", desc_list)
                
                target_row = date_matches[date_matches["Description"] == selected_desc].iloc[0]
                
                default_payer = str(target_row.get("Paid By", all_commuters[0])).strip()
                default_amount = float(target_row.get("Total Amount", 0.0))
                default_desc = str(target_row.get("Description", ""))
                
                raw_shares = str(target_row.get("Shared By", ""))
                default_shares = [s.strip() for s in raw_shares.split(",") if s.strip()]
                item_desc = default_desc
        else:
            item_desc = st.text_input("What was this for?", value="", placeholder="e.g., Office Lunch, Turf booking, Snacks")
            if not date_matches.empty and item_desc.strip():
                date_matches["Cleaned_Desc_Str"] = date_matches["Description"].astype(str).str.strip().str.lower()
                expense_exists = item_desc.strip().lower() in date_matches["Cleaned_Desc_Str"].values

        if expense_exists and not st.session_state.is_admin:
            st.markdown(
                """
                <div class='giant-lock-banner'>
                    <h1 style='font-size:75px;margin:0;'>🛑</h1>
                    <h2 style='font-size:38px;color:#EF4444;font-weight:900;margin:15px 0;line-height:1.2;'>Abe Loudu dubara expense kyun kar raha!</h2>
                    <h4 style='font-size:20px;color:#F1F5F9;font-weight:700;margin:0;'>Turn on 'Modify Existing Entry' above to edit this item safely.</h4>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            payer_idx = all_commuters.index(default_payer) if default_payer in all_commuters else 0
            payer = st.selectbox("Who Paid the Bill?", all_commuters, index=payer_idx, key="exp_payer")
            amount = st.number_input("Total Amount Spent (₹)", min_value=0.0, value=default_amount, step=50.0, key="exp_amount")
            
            if edit_mode and item_desc:
                st.info(f"✏️ Modifying description asset row: **{item_desc}**")

            st.markdown("#### 👥 Split Amount Among Whom?")
            selected_consumers = []
            cols = st.columns(len(all_commuters))
            for idx, person in enumerate(all_commuters):
                with cols[idx]:
                    is_checked = person in default_shares if edit_mode else True
                    if st.checkbox(person, value=is_checked, key=f"share_check_{person}"):
                        selected_consumers.append(person.strip().title())

            button_label = "📝 SAVE MODIFIED EXPENSE" if edit_mode else "💸 DISTRIBUTE & SAVE EXPENSE"
            
            if st.button(button_label):
                if amount <= 0.0 or not item_desc.strip() or len(selected_consumers) == 0:
                    st.error("🛑 Fill all details properly! Amount must be > 0 and at least one person chosen.")
                else:
                    with st.spinner("Saving expense ledger..."):
                        split_share = round(amount / len(selected_consumers), 2)
                        new_exp_row = pd.DataFrame([{"Date": str(exp_date), "Paid By": payer.strip().title(), "Total Amount": amount, "Description": item_desc.strip(), "Shared By": ", ".join(selected_consumers), "Per Head Cost": split_share}])
                        
                        # CLEAN OVERWRITE FOOTPRINT ENGINE: Bulletproof row filtration
                        if not df_exp_existing.empty:
                            df_exp_existing["Cleaned_Date_Str"] = df_exp_existing["Date"].astype(str).str.strip()
                            df_exp_existing["Cleaned_Desc_Str"] = df_exp_existing["Description"].astype(str).str.strip().str.lower()
                            
                            if edit_mode:
                                # Eliminate the specific old entry from database cache line entirely
                                df_exp_final = df_exp_existing[~(((df_exp_existing["Cleaned_Date_Str"] == t_dash_e) | (df_exp_existing["Cleaned_Date_Str"] == t_slash_e)) & (df_exp_existing["Cleaned_Desc_Str"] == item_desc.strip().lower()))]
                                df_exp_final = pd.concat([df_exp_final, new_exp_row], ignore_index=True)
                            else:
                                df_exp_final = pd.concat([df_exp_existing, new_exp_row], ignore_index=True)
                        else:
                            df_exp_final = new_exp_row
                        
                        # Wipe runtime lookup artifacts cleanly
                        if "Cleaned_Date_Str" in df_exp_final.columns: df_exp_final = df_exp_final.drop(columns=["Cleaned_Date_Str"])
                        if "Cleaned_Desc_Str" in df_exp_final.columns: df_exp_final = df_exp_final.drop(columns=["Cleaned_Desc_Str"])
                        
                        payload_exp = {"message": f"Log expense asset: {item_desc}", "content": base64.b64encode(df_exp_final.to_csv(index=False).encode("utf-8")).
