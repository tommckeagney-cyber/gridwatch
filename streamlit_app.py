import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime, timedelta
import folium
from folium import plugins
from streamlit.components.v1 import html
import time

st.set_page_config(page_title="GridWatch Ireland", page_icon="⚡", layout="wide")

# Import live scraper
from live_scraper import LiveScraper

# County coordinates
county_coords = {
    "Carlow": [52.8377, -6.9298], "Cavan": [53.9908, -7.3606],
    "Clare": [52.8627, -9.0259], "Cork": [51.8985, -8.4756],
    "Donegal": [54.6549, -8.1109], "Dublin": [53.3498, -6.2603],
    "Galway": [53.2707, -9.0568], "Kerry": [52.1546, -9.5231],
    "Kildare": [53.1584, -6.9028], "Kilkenny": [52.6538, -7.2493],
    "Laois": [53.0000, -7.3000], "Leitrim": [54.0000, -8.0000],
    "Limerick": [52.6638, -8.6267], "Longford": [53.7277, -7.7997],
    "Louth": [53.9257, -6.4827], "Mayo": [53.8378, -9.4001],
    "Meath": [53.6046, -6.6567], "Monaghan": [54.2500, -7.0000],
    "Offaly": [53.1000, -7.5000], "Roscommon": [53.6291, -8.1868],
    "Sligo": [54.2693, -8.4693], "Tipperary": [52.6807, -7.8246],
    "Waterford": [52.2593, -7.1101], "Westmeath": [53.5000, -7.5000],
    "Wexford": [52.4798, -6.4576], "Wicklow": [52.9915, -6.3647],
}

# Energy type colors
energy_colors = {
    "wind": "#3b82f6", "solar": "#eab308", "bess": "#22c55e",
    "grid": "#a855f7", "offshore": "#06b6d4", "biogas": "#f97316",
    "hydrogen": "#ec489a", "hydro": "#14b8a6", "data_centre": "#6b7280",
    "other": "#9ca3af", "unknown": "#9ca3af"
}

energy_icons = {
    "wind": "🌬️", "solar": "☀️", "bess": "🔋", "grid": "⚡",
    "offshore": "🌊", "biogas": "♻️", "hydrogen": "💧", "hydro": "💦",
    "data_centre": "🏢", "other": "🏭", "unknown": "❓"
}

# Load cached data
@st.cache_data(ttl=3600)
def load_cached_data():
    try:
        with open("data/cases.json", "r") as f:
            return json.load(f)
    except:
        return []

# Live scrape function
def scrape_date_range_with_progress(start_date, end_date):
    """Scrape data for a date range with progress updates"""
    scraper = LiveScraper()
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(message):
        status_text.text(message)
    
    # Run scraper
    cases = scraper.scrape_date_range(
        start_date, 
        end_date,
        progress_callback=update_progress
    )
    
    progress_bar.progress(100)
    status_text.text(f"✅ Found {len(cases)} energy cases!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()
    
    return cases

st.title("⚡ GridWatch Ireland")
st.markdown("### Energy Planning Intelligence Dashboard with Live Scraping")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/ireland.png", width=80)
    st.markdown("### About")
    st.markdown("Live scraping from An Coimisiún Pleanála")
    st.markdown("---")
    
    st.markdown("### 📅 Date Range")
    
    # Get date range for data
    cached_cases = load_cached_data()
    if cached_cases:
        df_cache = pd.DataFrame(cached_cases)
        df_cache['date_parsed'] = pd.to_datetime(df_cache['date_lodged'], errors='coerce')
        valid_dates = df_cache[df_cache['date_parsed'].notna()]['date_parsed']
        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
        else:
            min_date = datetime.now() - timedelta(days=365)
            max_date = datetime.now()
    else:
        min_date = datetime.now() - timedelta(days=365)
        max_date = datetime.now()
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "From",
            value=max_date - timedelta(days=30),
            min_value=min_date,
            max_value=max_date
        )
    with col2:
        end_date = st.date_input(
            "To",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
    
    # Live scrape button
    st.markdown("---")
    scrape_button = st.button(
        "🚀 Fetch Live Data", 
        use_container_width=True,
        help="Scrape the ACP website for this date range"
    )
    
    # Info about live scraping
    st.info("💡 **Tip:** Click 'Fetch Live Data' to get the latest applications for your date range. This may take 30-60 seconds.")
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    # We'll load filters after we have data

# Main content area
if scrape_button:
    # Convert to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    st.info(f"🔍 Fetching live data from {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}...")
    st.markdown("This may take 30-60 seconds while we scrape the ACP website.")
    
    # Scrape live data
    with st.spinner("Scraping planning applications..."):
        cases = scrape_date_range_with_progress(start_datetime, end_datetime)
    
    if cases:
        st.success(f"✅ Successfully retrieved {len(cases)} energy projects!")
        df_filtered = pd.DataFrame(cases)
        
        # Show in session state
        st.session_state['live_data'] = cases
        st.session_state['date_range'] = (start_date, end_date)
    else:
        st.warning("No energy projects found in this date range. Try a different range.")
        st.stop()

elif 'live_data' in st.session_state and st.session_state['date_range'][0] == start_date and st.session_state['date_range'][1] == end_date:
    # Use cached live data
    cases = st.session_state['live_data']
    df_filtered = pd.DataFrame(cases)
else:
    # Load cached data
    cases = load_cached_data()
    if cases:
        df = pd.DataFrame(cases)
        df['date_parsed'] = pd.to_datetime(df['date_lodged'], errors='coerce')
        
        # Filter by date range
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        df_filtered = df[
            (df['date_parsed'].notna()) & 
            (df['date_parsed'] >= start_datetime) & 
            (df['date_parsed'] <= end_datetime)
        ]
        
        if len(df_filtered) == 0:
            st.info(f"No cached data for {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}. Click 'Fetch Live Data' to scrape it.")
            st.stop()
    else:
        st.error("No data loaded. Click 'Fetch Live Data' to start scraping.")
        st.stop()

# Now apply sidebar filters
with st.sidebar:
    if len(df_filtered) > 0:
        selected_type = st.selectbox("Energy Type", ["All"] + sorted(df_filtered['energy_type'].unique().tolist()))
        selected_county = st.selectbox("County", ["All"] + sorted(df_filtered['county'].unique().tolist()))
        selected_status = st.selectbox("Status", ["All"] + sorted(df_filtered['status'].unique().tolist()))
    else:
        selected_type = "All"
        selected_county = "All"
        selected_status = "All"
        st.stop()

# Apply filters
if selected_type != "All":
    df_filtered = df_filtered[df_filtered['energy_type'] == selected_type]
if selected_county != "All":
    df_filtered = df_filtered[df_filtered['county'] == selected_county]
if selected_status != "All":
    df_filtered = df_filtered[df_filtered['status'] == selected_status]

# Sort by date
if 'date_parsed' in df_filtered.columns:
    df_filtered = df_filtered.sort_values('date_parsed', ascending=False)
else:
    df_filtered = df_filtered.sort_values('date_lodged', ascending=False)

# Stats Cards
st.subheader("📊 Project Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Projects", len(df_filtered))
with col2:
    st.metric("🌬️ Wind", len(df_filtered[df_filtered['energy_type'] == 'wind']))
with col3:
    st.metric("☀️ Solar", len(df_filtered[df_filtered['energy_type'] == 'solar']))
with col4:
    st.metric("🔋 BESS", len(df_filtered[df_filtered['energy_type'] == 'bess']))
with col5:
    st.metric("⚡ Grid", len(df_filtered[df_filtered['energy_type'] == 'grid']))

st.markdown("---")

# Map Section
st.subheader("🗺️ Project Locations")

col1, col2 = st.columns([3, 1])

with col1:
    # Create map
    m = folium.Map(location=[53.4129, -8.2439], zoom_start=7, control_scale=True)
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    
    # Add marker cluster
    marker_cluster = plugins.MarkerCluster(name='Projects').add_to(m)
    
    # Add markers
    for _, row in df_filtered.iterrows():
        lat = row.get('latitude')
        lon = row.get('longitude')
        
        if lat is None or pd.isna(lat):
            county = row.get('county', 'Unknown')
            if county in county_coords:
                lat, lon = county_coords[county]
            else:
                continue
        
        etype = row.get('energy_type', 'unknown')
        color = energy_colors.get(etype, '#9ca3af')
        icon = energy_icons.get(etype, '❓')
        
        has_exact = row.get('latitude') is not None and not pd.isna(row.get('latitude'))
        location_badge = "📍 Exact" if has_exact else "🏢 Approximate"
        
        status = row.get('status', '')
        if 'granted' in status.lower():
            status_emoji = "✅"
        elif 'pending' in status.lower() or 'lodged' in status.lower():
            status_emoji = "⏳"
        else:
            status_emoji = "📝"
        
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 250px;">
            <div style="background: {color}; padding: 8px; border-radius: 6px 6px 0 0; color: white;">
                <b>{icon} {row.get('energy_type', 'unknown').title()}</b>
                <span style="float: right; font-size: 10px;">{location_badge}</span>
            </div>
            <div style="padding: 12px;">
                <b>{row.get('title', 'No Title')[:100]}</b><br>
                <b>Ref:</b> {row.get('ref', 'N/A')}<br>
                <b>County:</b> {row.get('county', 'Unknown')}<br>
                <b>{status_emoji} Status:</b> {status}<br>
                <b>📅 Lodged:</b> {row.get('date_lodged', 'N/A')}<br>
                <a href="{row.get('source_url', '#')}" target="_blank" style="display: inline-block; margin-top: 8px; background: #2563eb; color: white; padding: 4px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">
                    🔗 View on pleanala.ie →
                </a>
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{icon} {row.get('title', '')[:50]}",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(marker_cluster)
    
    folium.LayerControl().add_to(m)
    map_html = m._repr_html_()
    html(map_html, height=500, width=700)

with col2:
    st.markdown("### 📍 Legend")
    for etype, color in energy_colors.items():
        count = len(df_filtered[df_filtered['energy_type'] == etype])
        icon = energy_icons.get(etype, "❓")
        st.markdown(
            f'<div style="display: flex; align-items: center; margin: 6px 0;">'
            f'<span style="display: inline-block; width: 16px; height: 16px; background: {color}; border-radius: 50%; margin-right: 8px;"></span>'
            f'<span>{icon} {etype.title()}: {count}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - **Click markers** to see project details
    - **Change date range** and click 'Fetch Live Data' to explore other periods
    - **Live scraping** gets the latest data from ACP
    """)

st.markdown("---")

# Charts
st.subheader("📈 Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Projects by Type")
    type_counts = df_filtered['energy_type'].value_counts()
    if len(type_counts) > 0:
        fig = px.pie(values=type_counts.values, names=type_counts.index, hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Projects by County")
    county_counts = df_filtered['county'].value_counts().head(10)
    if len(county_counts) > 0:
        fig = px.bar(x=county_counts.values, y=county_counts.index, orientation='h')
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Project Table
st.subheader("📋 Project List")

search = st.text_input("🔍 Search projects", placeholder="Search by title, reference, or county...")
if search:
    mask = (df_filtered['title'].str.contains(search, case=False, na=False) |
            df_filtered['ref'].str.contains(search, case=False, na=False) |
            df_filtered['county'].str.contains(search, case=False, na=False))
    df_filtered = df_filtered[mask]

display_cols = ['ref', 'title', 'county', 'energy_type', 'status', 'date_lodged']
available_cols = [c for c in display_cols if c in df_filtered.columns]

st.dataframe(
    df_filtered[available_cols],
    use_container_width=True,
    column_config={
        "ref": "Reference",
        "title": "Project Name",
        "county": "County",
        "energy_type": "Type",
        "status": "Status",
        "date_lodged": "Lodged Date",
    },
    height=400
)

# Download
csv = df_filtered.to_csv(index=False)
st.download_button("📥 Download CSV", csv, f"gridwatch_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv")

st.markdown("---")
st.caption(f"Showing {len(df_filtered)} projects | Data source: An Coimisiún Pleanála | Live scraping available")
