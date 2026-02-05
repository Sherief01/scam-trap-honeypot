import streamlit as st
import json, os, pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="SCAM-TRAP BEAST", layout="wide", page_icon="👹")

# --- CYBERPUNK STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0a0a0c; color: #e0e0e0; }
    .title-text { 
        color: #ff003c; 
        text-shadow: 2px 2px 10px #ff003c; 
        text-align: center; 
        font-size: 2.5rem; 
        font-weight: bold; 
        padding-bottom: 20px;
    }
    div[data-testid="stMetric"] { 
        background: rgba(20, 20, 25, 0.9); 
        border: 1px solid #ff003c; 
        border-radius: 5px; 
        padding: 15px; 
    }
    div[data-testid="stMetricLabel"] > div { color: #ffffff !important; font-weight: bold; }
    div[data-testid="stMetricValue"] > div { color: #ff003c !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-text">SCAM-TRAP: CYBER-CRIME INTEL CENTER v2.1</p>', unsafe_allow_html=True)

# Data Loading
LOG_FILE = "scam_log.json"

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        try:
            data = json.load(f)
        except:
            data = []

    if data:
        # --- METRICS ---
        c1, c2, c3 = st.columns(3)
        c1.metric("SCAMMERS TRAPPED", len(data))
        c2.metric("INTEL CAPTURED", sum(1 for d in data if d['intel'].get('upi_id') or d['intel'].get('phishing_links')))
        c3.metric("SYSTEM STATUS", "BEAST MODE 🔥")

        st.markdown("---")

        # --- DATABASE ---
        st.subheader("📊 Historical Intel Database")
        
        df_list = []
        for item in data:
            df_list.append({
                "Time": item.get('timestamp', 'N/A'),
                "Captured UPI": ", ".join(item['intel'].get('upi_id', [])),
                "Detected Link": ", ".join(item['intel'].get('phishing_links', [])),
                "Threat": item.get('threat_level', 'MEDIUM')
            })
        
        if df_list:
            df = pd.DataFrame(df_list)
            # ERROR FIXED: Explicitly using 'stretch' as per error message
            st.dataframe(df, width="stretch") 

        st.markdown("---")

        # --- LIVE FEED ---
        st.subheader("🔴 Real-Time Evidence Feed")
        for item in reversed(data):
            ts = item.get('timestamp', 'N/A')
            lvl = item.get('threat_level', 'GENERAL')
            
            with st.expander(f"EVENT: {ts} | THREAT: {lvl}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**👹 Scammer Message:**")
                    st.info(item.get('scammer_msg', 'No message content'))
                    st.markdown("**👵 Agent Saroja Paati:**")
                    st.success(item.get('paati_reply', 'No reply generated'))
                with col2:
                    st.markdown("**🔍 Intel Summary**")
                    st.error(f"UPI: {item['intel'].get('upi_id', 'None')}")
                    st.warning(f"URL: {item['intel'].get('phishing_links', 'None')}")
                    if st.button(f"Report ID {ts}", key=f"btn_{ts}"):
                        st.toast(f"Report {ts} submitted to Cyber Cell!")
    else:
        st.info("System Standby. Waiting for Scammers...")
else:
    st.warning("Evidence Log missing. Start the Backend API.")
