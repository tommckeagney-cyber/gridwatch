import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from folium import plugins
from streamlit.components.v1 import html

st.set_page_config(page_title="GridWatch Ireland", page_icon="⚡", layout="wide")

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1 {
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #f3f4f6;
        border-color: #667eea;
    }
    
    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Info box styling */
    .custom-info {
        background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
        border-left: 4px solid #667eea;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER SECTION ============
col1, col2 = st.columns([3, 1])
with col1:
    st.title("⚡ GridWatch Ireland")
    st.markdown("### 🇮🇪 Real-time Energy Planning Intelligence Dashboard")
with col2:
    st.image("https://img.icons8.com/color/96/ireland.png", width=100)

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

# ============ ENERGY STYLES ============
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

# ============ HELPER FUNCTIONS ============
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

@st.cache_data(ttl=3600)
def load_data():
    try:
        with open("data/cases.json", "r") as f:
            return json.load(f)
    except:
        return []

# ============ LOAD DATA ============
cases = load_data()

if not cases:
    st.error("No data loaded. Please contact administrator.")
    st.stop()

df = pd.DataFrame(cases)
df['energy_type'] = df['energy_type'].fillna('unknown')
df['county'] = df['county'].fillna('Unknown')
df['status'] = df['status'].fillna('Unknown')
df['title'] = df['title'].fillna('No Title')
df['date_parsed'] = df['date_lodged'].apply(parse_date)

# Get date range
valid_dates = df[df['date_parsed'].notna()]['date_parsed']
if len(valid_dates) > 0:
    min_date = valid_dates.min()
    max_date = valid_dates.max()
else:
    min_date = datetime.now() - timedelta(days=365)
    max_date = datetime.now()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 8px; color: white; margin-bottom: 1rem;">
        <strong>🎯 Mission:</strong><br>
        Monitoring energy planning applications across Ireland to provide real-time intelligence for developers, planners, and investors.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📅 Date Range Filter")
    
    start_date = st.date_input(
        "From",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    end_date = st.date_input(
        "To",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    st.markdown("**Quick select:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Last 7d", use_container_width=True):
            start_date = max_date - timedelta(days=7)
            end_date = max_date
            st.rerun()
    
    with col2:
        if st.button("Last 30d", use_container_width=True):
            start_date = max_date - timedelta(days=30)
            end_date = max_date
            st.rerun()
    
    with col3:
        if st.button("Last 90d", use_container_width=True):
            start_date = max_date - timedelta(days=90)
            end_date = max_date
            st.rerun()
    
    show_recent = st.checkbox("📅 Last 30 days only", value=True)
    if show_recent:
        start_date = max_date - timedelta(days=30)
        end_date = max_date
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    selected_type = st.selectbox("Energy Type", ["All"] + sorted(df['energy_type'].unique().tolist()))
    selected_county = st.selectbox("County", ["All"] + sorted(df['county'].unique().tolist()))
    selected_status = st.selectbox("Status", ["All"] + sorted(df['status'].unique().tolist()))
    
    st.markdown("---")
    st.caption(f"📅 Data range: {min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}")

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

if len(df_filtered) > 0:
    st.markdown(f"""
    <div class="custom-info">
        📅 Showing <strong>{len(df_filtered)}</strong> projects lodged between 
        <strong>{start_date.strftime('%d %B %Y')}</strong> and <strong>{end_date.strftime('%d %B %Y')}</strong>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning(f"No projects found in this date range. Try expanding the range.")

st.markdown("---")

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "📈 Analytics", "📋 Project Directory"])

# ============ TAB 1: MAP ============
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        m = folium.Map(location=[53.4129, -8.2439], zoom_start=7, control_scale=True)
        folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
        folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
        
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
            color = energy_colors.get(etype, '#9ca3af')
            icon = energy_icons.get(etype, '❓')
            title = row.get('title', 'No Title')[:100]
            ref = row.get('ref', 'N/A')
            county = row.get('county', 'Unknown')
            status = row.get('status', '')
            url = row.get('source_url', '#')
            
            # Enhanced popup
            popup_html = f"""
            <div style="font-family: 'Inter', sans-serif; min-width: 280px;">
                <div style="background: {color}; padding: 12px; border-radius: 8px 8px 0 0; color: white;">
                    <div style="font-size: 16px; font-weight: 600;">{icon} {etype.title()}</div>
                </div>
                <div style="padding: 16px; background: white;">
                    <div style="font-weight: 600; margin-bottom: 12px;">{title}</div>
                    <div style="font-size: 13px; color: #6b7280;">
                        <div><strong>Ref:</strong> {ref}</div>
                        <div><strong>County:</strong> {county}</div>
                        <div><strong>Status:</strong> {status}</div>
                    </div>
                    <a href="{url}" target="_blank" 
                       style="display: inline-block; margin-top: 12px; 
                              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 8px 16px; text-decoration: none; 
                              border-radius: 6px; font-weight: 500;">
                        🔗 View Details →
                    </a>
                </div>
            </div>
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{icon} {title[:50]}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(marker_cluster)
        
        folium.LayerControl().add_to(m)
        map_html = m._repr_html_()
        html(map_html, height=550, width=700)
    
    with col2:
        st.markdown("### 📍 Legend")
        for etype, color in energy_colors.items():
            count = len(df_filtered[df_filtered['energy_type'] == etype])
            icon = energy_icons.get(etype, "❓")
            st.markdown(
                f'<div style="display: flex; align-items: center; margin: 8px 0;">'
                f'<span style="display: inline-block; width: 16px; height: 16px; background: {color}; border-radius: 50%; margin-right: 10px;"></span>'
                f'<span>{icon} {etype.title()}: <strong>{count}</strong></span>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        st.markdown("### 💡 Map Tips")
        st.markdown("""
        - **Click markers** for project details
        - **Zoom in/out** with mouse wheel
        - **Use layer control** (top right) to change map style
        - **Clusters** show multiple projects in same area
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.markdown(f"**Total on map:** {len(df_filtered)} projects")
        st.markdown(f"**Counties:** {df_filtered['county'].nunique()}")
        st.markdown(f"**Energy types:** {df_filtered['energy_type'].nunique()}")

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
                marker=dict(
                    colors=[energy_colors.get(t, '#9ca3af') for t in type_counts.index],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent',
                textfont_size=12
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=450,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    with col2:
        st.markdown("#### 📊 Projects by County")
        county_counts = df_filtered['county'].value_counts().head(10)
        if len(county_counts) > 0:
            fig = go.Figure(data=[go.Bar(
                x=county_counts.values,
                y=county_counts.index,
                orientation='h',
                marker=dict(
                    color=county_counts.values,
                    colorscale='Viridis',
                    line=dict(color='white', width=1)
                ),
                text=county_counts.values,
                textposition='outside'
            )])
            fig.update_layout(
                title="Top 10 Counties",
                xaxis_title="Number of Projects",
                yaxis_title="County",
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
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
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#764ba2'),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)'
            )])
            fig.update_layout(
                title="Project Applications by Date",
                xaxis_title="Date",
                yaxis_title="Number of Applications",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for timeline chart")
    
    with col2:
        st.markdown("#### 📊 Status Distribution")
        status_counts = df_filtered['status'].value_counts()
        if len(status_counts) > 0:
            fig = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3,
                marker=dict(line=dict(color='white', width=2)),
                textinfo='label+percent'
            )])
            fig.update_layout(
                title="Project Status Breakdown",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

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
        height=500
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df_display.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"gridwatch_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            use_container_width=True
        )
    
    with col2:
        json_str = df_display.to_json(orient='records', indent=2)
        st.download_button(
            "📥 Download JSON",
            json_str,
            f"gridwatch_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json",
            use_container_width=True
        )

# ============ FOOTER ============
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: gray; font-size: 12px;">
        <b>⚡ GridWatch Ireland</b> | Data from An Coimisiún Pleanála<br>
        Showing {len(df_filtered)} projects from {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}<br>
        Data updates weekly | Built with Streamlit | 🇮🇪 Powering Ireland's Energy Transition
    </div>
    """,
    unsafe_allow_html=True
)
