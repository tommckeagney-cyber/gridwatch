import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from folium import plugins
from streamlit.components.v1 import html

st.set_page_config(
    page_title="GridWatch Ireland",
    page_icon="⚡",
    layout="wide"
)

# ============ DARK THEME CSS WITH FIXED SIDEBAR ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a12 0%, #14141f 100%);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    .gradient-header {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0;
    }
    
    .subtitle {
        color: #cbd5e1 !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .animated-border {
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
        background-size: 200% 200%;
        animation: gradient 3s ease infinite;
        height: 3px;
        width: 100%;
        border-radius: 3px;
        margin: 1rem 0;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(30, 30, 46, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #60a5fa;
    }
    
    [data-testid="stMetric"] label {
        color: #cbd5e1 !important;
        font-weight: 600;
    }
    
    [data-testid="stMetric"] .stMetricValue {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(96, 165, 250, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(30, 30, 46, 0.8);
        backdrop-filter: blur(10px);
        padding: 8px;
        border-radius: 60px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 40px;
        padding: 10px 28px;
        font-weight: 600;
        color: #cbd5e1 !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
    }
    
    /* ============ FIXED SIDEBAR ============ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f18 0%, #181824 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] p {
        color: #cbd5e1 !important;
    }
    
    /* Sidebar select boxes - FIXED */
    [data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #1e1e2e !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
        color: #f0f0f0 !important;
    }
    
    /* Sidebar date inputs - FIXED */
    [data-testid="stSidebar"] .stDateInput label {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stDateInput input {
        background-color: #1e1e2e !important;
        color: #f0f0f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    /* Sidebar checkbox - FIXED */
    [data-testid="stSidebar"] .stCheckbox label {
        color: #ffffff !important;
    }
    
    /* Sidebar caption text */
    [data-testid="stSidebar"] .stCaption {
        color: #9ca3af !important;
    }
    
    /* Sidebar info/alert boxes */
    [data-testid="stSidebar"] .stAlert {
        background-color: #1e1e2e !important;
        color: #e2e8f0 !important;
    }
    
    /* General select boxes (non-sidebar) */
    .stSelectbox label {
        color: #cbd5e1 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1e1e2e !important;
        border: 1px solid #334155 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] div {
        color: #f0f0f0 !important;
    }
    
    /* Date inputs */
    .stDateInput label {
        color: #cbd5e1 !important;
    }
    
    .stDateInput input {
        background-color: #1e1e2e !important;
        color: #f0f0f0 !important;
        border: 1px solid #334155 !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #cbd5e1 !important;
    }
    
    /* Info box */
    .custom-info {
        background: rgba(30, 30, 46, 0.95);
        border-left: 4px solid #60a5fa;
        padding: 16px 20px;
        border-radius: 16px;
        margin: 20px 0;
        color: #e2e8f0 !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background: rgba(30, 30, 46, 0.8);
        border-radius: 16px;
    }
    
    .stDataFrame table {
        color: #e2e8f0 !important;
    }
    
    .stDataFrame th {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
    }
    
    .stDataFrame td {
        color: #cbd5e1 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #6b7280 !important;
        font-size: 12px;
        padding: 1rem;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin-top: 2rem;
    }
    
    /* Caption and small text */
    .stCaption, caption {
        color: #9ca3af !important;
    }
    
    /* Warning and info messages */
    .stAlert {
        background-color: rgba(30, 30, 46, 0.95) !important;
        color: #e2e8f0 !important;
    }
    
    /* Metric delta */
    [data-testid="stMetricDelta"] {
        color: #86efac !important;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown('<h1 class="gradient-header">⚡ GridWatch Ireland</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Energy Planning Intelligence Dashboard</p>', unsafe_allow_html=True)
st.markdown('<div class="animated-border"></div>', unsafe_allow_html=True)

# ============ LOAD DATA ============
@st.cache_data(ttl=3600)
def load_data():
    try:
        with open("data/cases.json", "r") as f:
            return json.load(f)
    except:
        return []

cases = load_data()

if not cases:
    st.error("No data loaded. Please run the scraper first.")
    st.stop()

df = pd.DataFrame(cases)
df['energy_type'] = df['energy_type'].fillna('unknown')
df['county'] = df['county'].fillna('Unknown')
df['status'] = df['status'].fillna('Unknown')
df['title'] = df['title'].fillna('No Title')

def parse_date(date_str):
    if not date_str or date_str == 'Unknown':
        return None
    try:
        return datetime.strptime(date_str, '%d/%m/%Y')
    except:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None

df['date_parsed'] = df['date_lodged'].apply(parse_date)

valid_dates = df[df['date_parsed'].notna()]['date_parsed']
if len(valid_dates) > 0:
    data_min_date = valid_dates.min()
    data_max_date = valid_dates.max()
else:
    data_min_date = datetime.now() - timedelta(days=365)
    data_max_date = datetime.now()

default_start = data_max_date - timedelta(days=30)
default_end = data_max_date

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🎯 Dashboard")
    st.markdown("Monitoring energy planning applications across Ireland.")
    st.markdown("---")
    
    st.markdown("### 📅 Date Range")
    
    start_date = st.date_input(
        "From",
        value=default_start,
        min_value=data_min_date,
        max_value=data_max_date,
        format="DD/MM/YYYY"
    )
    
    end_date = st.date_input(
        "To",
        value=default_end,
        min_value=data_min_date,
        max_value=data_max_date,
        format="DD/MM/YYYY"
    )
    
    st.markdown("**Quick Select:**")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("7d", use_container_width=True):
            start_date = data_max_date - timedelta(days=7)
            end_date = data_max_date
            st.rerun()
    with q2:
        if st.button("30d", use_container_width=True):
            start_date = data_max_date - timedelta(days=30)
            end_date = data_max_date
            st.rerun()
    with q3:
        if st.button("90d", use_container_width=True):
            start_date = data_max_date - timedelta(days=90)
            end_date = data_max_date
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    selected_type = st.selectbox("Energy Type", ["All"] + sorted(df['energy_type'].unique().tolist()))
    selected_county = st.selectbox("County", ["All"] + sorted(df['county'].unique().tolist()))
    selected_status = st.selectbox("Status", ["All"] + sorted(df['status'].unique().tolist()))
    
    st.markdown("---")
    st.caption(f"📊 Database: {len(df)} total projects")
    st.caption(f"📅 Data range: {data_min_date.strftime('%d/%m/%Y')} - {data_max_date.strftime('%d/%m/%Y')}")

# ============ APPLY FILTERS ============
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

df_filtered = df[
    (df['date_parsed'].notna()) & 
    (df['date_parsed'] >= start_datetime) & 
    (df['date_parsed'] <= end_datetime)
]

if selected_type != "All":
    df_filtered = df_filtered[df_filtered['energy_type'] == selected_type]
if selected_county != "All":
    df_filtered = df_filtered[df_filtered['county'] == selected_county]
if selected_status != "All":
    df_filtered = df_filtered[df_filtered['status'] == selected_status]

df_filtered = df_filtered.sort_values('date_parsed', ascending=False)

# ============ STATS CARDS ============
st.subheader("📊 Key Metrics")

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric("Total Projects", len(df_filtered))
with m2:
    st.metric("🌬️ Wind", len(df_filtered[df_filtered['energy_type'] == 'wind']))
with m3:
    st.metric("☀️ Solar", len(df_filtered[df_filtered['energy_type'] == 'solar']))
with m4:
    st.metric("🔋 BESS", len(df_filtered[df_filtered['energy_type'] == 'bess']))
with m5:
    st.metric("⚡ Grid", len(df_filtered[df_filtered['energy_type'] == 'grid']))

if len(df_filtered) > 0:
    st.markdown(f"""
    <div class="custom-info">
        📅 Showing <strong>{len(df_filtered)}</strong> projects lodged between 
        <strong>{start_date.strftime('%d/%m/%Y')}</strong> and <strong>{end_date.strftime('%d/%m/%Y')}</strong>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No projects found in this date range. Try expanding the range.")

st.markdown("---")

# ============ COUNTY COORDINATES ============
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

energy_colors = {
    "wind": "#60a5fa", "solar": "#fbbf24", "bess": "#34d399",
    "grid": "#c084fc", "offshore": "#2dd4bf", "biogas": "#fb923c",
    "hydrogen": "#f472b6", "hydro": "#2dd4bf", "data_centre": "#6b7280",
    "other": "#9ca3af", "unknown": "#6b7280"
}

energy_icons = {
    "wind": "🌬️", "solar": "☀️", "bess": "🔋", "grid": "⚡",
    "offshore": "🌊", "biogas": "♻️", "hydrogen": "💧", "hydro": "💦",
    "data_centre": "🏢", "other": "🏭", "unknown": "❓"
}

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "📈 Analytics", "📋 Project Directory"])

# ============ TAB 1: MAP ============
with tab1:
    map_col1, map_col2 = st.columns([3, 1])
    
    with map_col1:
        if len(df_filtered) > 0:
            m = folium.Map(location=[53.4129, -8.2439], zoom_start=7, control_scale=True)
            folium.TileLayer('CartoDB dark_matter', name='Dark').add_to(m)
            folium.TileLayer('OpenStreetMap', name='Street').add_to(m)
            
            marker_cluster = plugins.MarkerCluster(name='Projects').add_to(m)
            
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
                color = energy_colors.get(etype, '#6b7280')
                icon = energy_icons.get(etype, '❓')
                
                popup_html = f"""
                <div style="font-family: 'Inter', sans-serif; min-width: 260px; background: #1a1a2a; border-radius: 12px; overflow: hidden;">
                    <div style="background: {color}; padding: 10px; color: white;">
                        <b>{icon} {row.get('energy_type', 'unknown').title()}</b>
                    </div>
                    <div style="padding: 12px;">
                        <div style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">{row.get('title', 'No Title')[:100]}</div>
                        <div style="color: #cbd5e1; font-size: 12px;">
                            📋 {row.get('ref', 'N/A')}<br>
                            📍 {row.get('county', 'Unknown')}<br>
                            📅 {row.get('date_lodged', 'N/A')}<br>
                            📊 {row.get('status', 'Unknown')}
                        </div>
                        <a href="{row.get('source_url', '#')}" target="_blank" 
                           style="display: inline-block; margin-top: 10px; 
                                  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); 
                                  color: white; padding: 5px 12px; text-decoration: none; 
                                  border-radius: 6px; font-size: 12px;">
                            🔗 View Details →
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
            html(map_html, height=550, width=700)
        else:
            st.info("No projects to display on map. Try adjusting filters.")
    
    with map_col2:
        st.markdown("### 📍 Legend")
        for etype, color in energy_colors.items():
            count = len(df_filtered[df_filtered['energy_type'] == etype])
            icon = energy_icons.get(etype, "❓")
            if count > 0 or etype in ['wind', 'solar', 'bess', 'grid']:
                st.markdown(
                    f'<div style="display: flex; align-items: center; margin: 8px 0;">'
                    f'<span style="display: inline-block; width: 14px; height: 14px; background: {color}; border-radius: 50%; margin-right: 10px;"></span>'
                    f'<span style="color: #e2e8f0;">{icon} {etype.title()}</span>'
                    f'<span style="margin-left: auto; background: #2d2d3a; padding: 2px 8px; border-radius: 20px; font-size: 11px; color: #94a3b8;">{count}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - 🖱️ **Click markers** for project details
        - 🔍 **Zoom in/out** with mouse wheel
        - 🗺️ **Layer control** (top right) to change map style
        - 📍 **Clusters** show multiple projects in same area
        """)
        
        st.markdown("---")
        st.markdown(f"**📍 Projects on map:** {len(df_filtered)}")
        st.markdown(f"**🏙️ Counties:** {df_filtered['county'].nunique()}")

# ============ TAB 2: ANALYTICS ============
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥧 Projects by Type")
        type_counts = df_filtered['energy_type'].value_counts()
        if len(type_counts) > 0:
            fig = go.Figure(data=[go.Pie(
                labels=type_counts.index,
                values=type_counts.values,
                hole=0.4,
                marker=dict(colors=[energy_colors.get(t, '#6b7280') for t in type_counts.index]),
                textinfo='label+percent',
                textfont=dict(color='#ffffff', size=12)
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=450,
                font=dict(color='#ffffff')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Top Counties")
        county_counts = df_filtered['county'].value_counts().head(10)
        if len(county_counts) > 0:
            fig = go.Figure(data=[go.Bar(
                x=county_counts.values,
                y=county_counts.index,
                orientation='h',
                marker=dict(color=county_counts.values, colorscale='Viridis'),
                text=county_counts.values,
                textposition='outside',
                textfont=dict(color='#ffffff')
            )])
            fig.update_layout(
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                xaxis_title="Number of Projects",
                yaxis_title="County",
                xaxis=dict(tickfont=dict(color='#ffffff')),
                yaxis=dict(tickfont=dict(color='#ffffff'))
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Applications Over Time")
        if len(df_filtered) > 0:
            df_filtered['date_week'] = df_filtered['date_parsed'].dt.strftime('%Y-%m-%d')
            timeline = df_filtered.groupby('date_week').size().reset_index(name='count')
            timeline = timeline.sort_values('date_week')
            
            fig = go.Figure(data=[go.Scatter(
                x=timeline['date_week'],
                y=timeline['count'],
                mode='lines+markers',
                line=dict(color='#60a5fa', width=3),
                marker=dict(size=8, color='#a78bfa'),
                fill='tozeroy',
                fillcolor='rgba(96, 165, 250, 0.2)'
            )])
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Applications",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                xaxis=dict(tickfont=dict(color='#ffffff')),
                yaxis=dict(tickfont=dict(color='#ffffff'))
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Status Distribution")
        status_counts = df_filtered['status'].value_counts()
        if len(status_counts) > 0:
            fig = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3,
                textinfo='label+percent',
                textfont=dict(color='#ffffff', size=12)
            )])
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff')
            )
            st.plotly_chart(fig, use_container_width=True)

# ============ TAB 3: PROJECT DIRECTORY ============
with tab3:
    search = st.text_input("🔍 Search projects", placeholder="Search by title, reference, or county...")
    df_display = df_filtered.copy()
    
    if search:
        mask = (df_display['title'].str.contains(search, case=False, na=False) |
                df_display['ref'].str.contains(search, case=False, na=False) |
                df_display['county'].str.contains(search, case=False, na=False))
        df_display = df_display[mask]
        st.caption(f"Found {len(df_display)} projects matching '{search}'")
    
    display_cols = ['ref', 'title', 'county', 'energy_type', 'status', 'date_lodged']
    available_cols = [c for c in display_cols if c in df_display.columns]
    
    st.dataframe(
        df_display[available_cols],
        use_container_width=True,
        column_config={
            "ref": st.column_config.TextColumn("Reference", width="small"),
            "title": st.column_config.TextColumn("Project Name", width="large"),
            "county": st.column_config.TextColumn("County", width="medium"),
            "energy_type": st.column_config.TextColumn("Type", width="small"),
            "status": st.column_config.TextColumn("Status", width="medium"),
            "date_lodged": st.column_config.TextColumn("Lodged", width="small"),
        },
        height=400
    )
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df_display.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, f"gridwatch_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv", use_container_width=True)
    
    with col2:
        json_str = df_display.to_json(orient='records', indent=2)
        st.download_button("📥 Download JSON", json_str, f"gridwatch_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json", use_container_width=True)

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    ⚡ GridWatch Ireland | Data from An Coimisiún Pleanála | Data updates weekly
</div>
""", unsafe_allow_html=True)
