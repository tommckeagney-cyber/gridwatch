import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="GridWatch Ireland", page_icon="⚡", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    try:
        with open("data/cases.json", "r") as f:
            return json.load(f)
    except:
        return []

st.title("⚡ GridWatch Ireland")
st.markdown("### Energy Planning Intelligence Dashboard")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/ireland.png", width=80)
    st.markdown("### About")
    st.markdown("Monitoring energy planning applications across Ireland.")
    st.markdown("**Data Source:** An Coimisiún Pleanála")
    st.markdown("---")
    st.caption(f"Updated: {datetime.now().strftime("%Y-%m-%d")}")

cases = load_data()

if not cases:
    st.error("No data loaded. Please contact administrator.")
    st.stop()

df = pd.DataFrame(cases)
df["energy_type"] = df["energy_type"].fillna("unknown")
df["county"] = df["county"].fillna("Unknown")
df["status"] = df["status"].fillna("Unknown")

with st.sidebar:
    st.markdown("### Filters")
    selected_type = st.selectbox("Energy Type", ["All"] + sorted(df["energy_type"].unique().tolist()))
    selected_county = st.selectbox("County", ["All"] + sorted(df["county"].unique().tolist()))
    selected_status = st.selectbox("Status", ["All"] + sorted(df["status"].unique().tolist()))

df_filtered = df.copy()
if selected_type != "All":
    df_filtered = df_filtered[df_filtered["energy_type"] == selected_type]
if selected_county != "All":
    df_filtered = df_filtered[df_filtered["county"] == selected_county]
if selected_status != "All":
    df_filtered = df_filtered[df_filtered["status"] == selected_status]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Projects", len(df_filtered))
with col2:
    st.metric("🌬️ Wind", len(df_filtered[df_filtered["energy_type"] == "wind"]))
with col3:
    st.metric("☀️ Solar", len(df_filtered[df_filtered["energy_type"] == "solar"]))
with col4:
    st.metric("🔋 BESS", len(df_filtered[df_filtered["energy_type"] == "bess"]))
with col5:
    st.metric("⚡ Grid", len(df_filtered[df_filtered["energy_type"] == "grid"]))

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Projects by Type")
    type_counts = df_filtered["energy_type"].value_counts()
    if len(type_counts) > 0:
        fig = px.pie(values=type_counts.values, names=type_counts.index, hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Counties")
    county_counts = df_filtered["county"].value_counts().head(10)
    if len(county_counts) > 0:
        fig = px.bar(x=county_counts.values, y=county_counts.index, orientation="h")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("📋 Project List")

search = st.text_input("🔍 Search", placeholder="Search by title, reference, or county...")
if search:
    mask = (df_filtered["title"].str.contains(search, case=False, na=False) |
            df_filtered["ref"].str.contains(search, case=False, na=False) |
            df_filtered["county"].str.contains(search, case=False, na=False))
    df_filtered = df_filtered[mask]

display_cols = ["ref", "title", "county", "energy_type", "status", "date_lodged"]
available_cols = [c for c in display_cols if c in df_filtered.columns]
st.dataframe(df_filtered[available_cols], use_container_width=True)

csv = df_filtered.to_csv(index=False)
st.download_button("📥 Download CSV", csv, f"gridwatch_{datetime.now().strftime("%Y-%m-%d")}.csv")

st.markdown("---")
st.caption("Data from An Coimisiún Pleanála | Built with Streamlit")
