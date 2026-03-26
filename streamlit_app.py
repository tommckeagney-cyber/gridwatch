import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="GridWatch Test", page_icon="⚡")

st.title("⚡ GridWatch Ireland - Test Page")
st.write("If you can see this, the deployment is working!")

# Try to load data
try:
    with open("data/cases.json", "r") as f:
        cases = json.load(f)
    st.success(f"✅ Found {len(cases)} cases in data/cases.json")
    
    # Show first 5
    if cases:
        st.subheader("First 5 projects:")
        for case in cases[:5]:
            st.write(f"- {case.get('title', 'No title')} ({case.get('ref', 'No ref')})")
            
except FileNotFoundError:
    st.error("❌ data/cases.json not found!")
    st.info("Make sure the data folder exists with cases.json")

st.write("---")
st.write("Deployment working! Now we can add the full dashboard.")
