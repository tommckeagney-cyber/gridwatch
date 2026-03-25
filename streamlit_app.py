import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
import folium
from folium import plugins
from streamlit_folium import st_folium

# Page config
st.set_page_config(page_title="GridWatch Ireland", page_icon="⚡", layout="wide")

# County coordinates for Ireland
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

# Energy type colors and icons
energy_styles = {
    "wind": {"color": "#3b82f6", "icon": "🌬️", "name": "Wind Farm"},
    "solar": {"color": "#eab308", "icon": "☀️", "name": "Solar Farm"},
    "bess": {"color": "#22c55e", "icon": "🔋", "name": "Battery Storage"},
    "grid": {"color": "#a855f7", "icon": "⚡", "name": "Grid Infrastructure"},
    "offshore": {"color": "#06b6d4", "icon": "🌊", "name": "Offshore Wind"},
    "biogas": {"color": "#f97316", "icon": "♻️", "name": "Biogas/Biomass"},
    "hydrogen": {"color": "#ec489a", "icon": "💧", "name": "Hydrogen"},
    "hydro": {"color": "#14b8a6", "icon": "💦", "name": "Hydroelectric"},
    "data_centre": {"color": "#6b7280", "icon": "🏢", "name": "Data Centre"},
    "other": {"color": "#9ca3af", "icon": "🏭", "name": "Other Energy"},
    "unknown": {"color": "#9ca3af", "icon": "❓", "name": "Unknown"}
}

# Load data
@st.cache_data(ttl=3600)
def load_data():
    try:
        with open("data/cases.json", "r") as f:
            return json.load(f)
    except:
        return []

# Title
st.title("⚡ GridWatch Ireland")
st.markdown("### Energy Planning Intelligence Dashboard with Interactive Map")
st.markdown("---")

# Load data
cases = load_data()

if not cases:
    st.error("No data loaded. Please contact administrator.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(cases)
df['energy_type'] = df['energy_type'].fillna('unknown')
df['county'] = df['county'].fillna('Unknown')
df['status'] = df['status'].fillna('Unknown')
df['title'] = df['title'].fillna('No Title')

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/ireland.png", width=80)
    st.markdown("### About GridWatch")
    st.markdown("""
    **GridWatch Ireland** monitors energy planning applications across Ireland.
    
    **Data Source:** An Coimisiún Pleanála (pleanala.ie)
    
    **Project Types Tracked:**
    - 🌬️ Wind Farms (Onshore & Offshore)
    - ☀️ Solar Farms
    - 🔋 Battery Storage (BESS)
    - ⚡ Grid Infrastructure
    - ♻️ Biogas & Biomass
    - 💧 Hydrogen Projects
    - 💦 Hydroelectric
    """)
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    # Filters
    selected_type = st.selectbox("Energy Type", ["All"] + sorted(df['energy_type'].unique().tolist()))
    selected_county = st.selectbox("County", ["All"] + sorted(df['county'].unique().tolist()))
    selected_status = st.selectbox("Status", ["All"] + sorted(df['status'].unique().tolist()))
    
    st.markdown("---")
    st.caption(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Apply filters
df_filtered = df.copy()
if selected_type != "All":
    df_filtered = df_filtered[df_filtered['energy_type'] == selected_type]
if selected_county != "All":
    df_filtered = df_filtered[df_filtered['county'] == selected_county]
if selected_status != "All":
    df_filtered = df_filtered[df_filtered['status'] == selected_status]

# Stats Cards
st.subheader("📊 Project Statistics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Projects", len(df_filtered), delta=None)
with col2:
    wind_count = len(df_filtered[df_filtered['energy_type'] == 'wind'])
    st.metric("🌬️ Wind", wind_count)
with col3:
    solar_count = len(df_filtered[df_filtered['energy_type'] == 'solar'])
    st.metric("☀️ Solar", solar_count)
with col4:
    bess_count = len(df_filtered[df_filtered['energy_type'] == 'bess'])
    st.metric("🔋 BESS", bess_count)
with col5:
    grid_count = len(df_filtered[df_filtered['energy_type'] == 'grid'])
    st.metric("⚡ Grid", grid_count)

st.markdown("---")

# Map Section
st.subheader("🗺️ Interactive Map of Energy Projects")

# Create two columns for map and legend
col1, col2 = st.columns([3, 1])

with col1:
    # Create base map centered on Ireland
    m = folium.Map(location=[53.4129, -8.2439], zoom_start=7, control_scale=True)
    
    # Add different map styles
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)
    
    # Add marker cluster for better performance
    marker_cluster = plugins.MarkerCluster(
        name='Projects',
        options={'maxClusterRadius': 40, 'spiderfyOnMaxZoom': True}
    ).add_to(m)
    
    # Add markers for each project
    for _, row in df_filtered.iterrows():
        county = row.get('county', 'Unknown')
        if county in county_coords:
            lat, lon = county_coords[county]
            etype = row.get('energy_type', 'unknown')
            style = energy_styles.get(etype, energy_styles['unknown'])
            
            # Determine status emoji
            status = row.get('status', '')
            if 'granted' in status.lower() or 'approved' in status.lower():
                status_emoji = "✅"
            elif 'pending' in status.lower() or 'lodged' in status.lower():
                status_emoji = "⏳"
            elif 'refused' in status.lower() or 'rejected' in status.lower():
                status_emoji = "❌"
            else:
                status_emoji = "📝"
            
            # Create popup HTML
            popup_html = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; min-width: 250px; max-width: 300px;">
                <div style="background: {style['color']}; padding: 8px; border-radius: 6px 6px 0 0; color: white;">
                    <b>{style['icon']} {style['name']}</b>
                </div>
                <div style="padding: 12px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b;">{row.get('title', 'No Title')[:100]}</h4>
                    <p style="margin: 4px 0;"><b>📋 Ref:</b> {row.get('ref', 'N/A')}</p>
                    <p style="margin: 4px 0;"><b>📍 County:</b> {county}</p>
                    <p style="margin: 4px 0;"><b>{status_emoji} Status:</b> {status}</p>
                    <p style="margin: 4px 0;"><b>📅 Lodged:</b> {row.get('date_lodged', 'N/A')}</p>
            """
            
            if row.get('mw_capacity'):
                popup_html += f'<p style="margin: 4px 0;"><b>⚡ Capacity:</b> {row["mw_capacity"]} MW</p>'
            
            popup_html += f"""
                    <hr style="margin: 8px 0;">
                    <a href="{row.get('source_url', '#')}" target="_blank" style="display: inline-block; background: #2563eb; color: white; padding: 4px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">
                        🔗 View on pleanala.ie →
                    </a>
                </div>
            </div>
            """
            
            # Add circle marker with color based on energy type
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{style['icon']} {row.get('title', '')[:50]}",
                color=style['color'],
                fill=True,
                fillColor=style['color'],
                fillOpacity=0.7,
                weight=2,
                opacity=1
            ).add_to(marker_cluster)
    
    # Add layer control
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen(position='topright').add_to(m)
    
    # Display the map
    st_data = st_folium(m, width=700, height=500, key="map")

with col2:
    st.markdown("### 📍 Map Legend")
    st.markdown("---")
    
    # Show legend with counts
    for etype, style in energy_styles.items():
        count = len(df_filtered[df_filtered['energy_type'] == etype])
        if count > 0 or etype in ['wind', 'solar', 'bess', 'grid']:  # Show main types always
            st.markdown(
                f'<div style="display: flex; align-items: center; margin: 8px 0;">'
                f'<span style="display: inline-block; width: 16px; height: 16px; background: {style["color"]}; border-radius: 50%; margin-right: 8px;"></span>'
                f'<span><b>{style["icon"]} {style["name"]}</b> <span style="color: #666;">({count})</span></span>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    st.markdown("### 💡 Map Tips")
    st.markdown("""
    - **Click markers** to see project details
    - **Zoom in/out** for better view
    - **Use layer control** (top right) to change map style
    - **Hover** over markers to see project name
    - **Cluster groups** show multiple projects in same area
    """)
    
    # Show summary of filtered data
    st.markdown("---")
    st.markdown("### 📊 Current View")
    st.markdown(f"**Showing:** {len(df_filtered)} projects")
    st.markdown(f"**Counties:** {df_filtered['county'].nunique()}")
    st.markdown(f"**Energy Types:** {df_filtered['energy_type'].nunique()}")

st.markdown("---")

# Charts Section
st.subheader("📈 Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Projects by Type")
    type_counts = df_filtered['energy_type'].value_counts()
    if len(type_counts) > 0:
        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Top 10 Counties")
    county_counts = df_filtered['county'].value_counts().head(10)
    if len(county_counts) > 0:
        fig = px.bar(
            x=county_counts.values,
            y=county_counts.index,
            orientation='h',
            color=county_counts.values,
            color_continuous_scale='Blues',
            text=county_counts.values
        )
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Project List Section
st.subheader("📋 Detailed Project List")

# Search box
search = st.text_input("🔍 Search projects", placeholder="Search by title, reference, or county...")
if search:
    mask = (df_filtered['title'].str.contains(search, case=False, na=False) |
            df_filtered['ref'].str.contains(search, case=False, na=False) |
            df_filtered['county'].str.contains(search, case=False, na=False))
    df_filtered = df_filtered[mask]
    st.caption(f"Found {len(df_filtered)} projects matching '{search}'")

# Display table
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

# Download buttons
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"gridwatch_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    json_str = df_filtered.to_json(orient='records', indent=2)
    st.download_button(
        label="📥 Download as JSON",
        data=json_str,
        file_name=f"gridwatch_{datetime.now().strftime('%Y-%m-%d')}.json",
        mime="application/json",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px;">
        <b>⚡ GridWatch Ireland</b> | Data from An Coimisiún Pleanála (pleanala.ie)<br>
        Built with Streamlit & Folium | Data updates weekly | Interactive map shows project locations by county
    </div>
    """,
    unsafe_allow_html=True
)
