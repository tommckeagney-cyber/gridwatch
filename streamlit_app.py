import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from folium import plugins
from streamlit.components.v1 import html
import anthropic
import random

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="GridWatch Ireland",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ MODERN CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Glassmorphism effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
    }
    
    /* Gradient header */
    .gradient-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3rem;
    }
    
    /* Animated gradient border */
    .animated-border {
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        background-size: 200% 200%;
        animation: gradient 3s ease infinite;
        height: 3px;
        width: 100%;
        border-radius: 3px;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Modern metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.98) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stMetric"] label {
        font-weight: 600;
        color: #1e293b;
    }
    
    [data-testid="stMetric"] .stMetricValue {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(248, 250, 252, 0.8);
        backdrop-filter: blur(10px);
        padding: 8px;
        border-radius: 60px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 40px;
        padding: 10px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Modern sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Info box animation */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .custom-info {
        background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
        border-left: 4px solid #667eea;
        padding: 16px 20px;
        border-radius: 16px;
        margin: 20px 0;
        animation: slideIn 0.5s ease;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-text {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* AI insight card */
    .ai-insight {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid #c4b5fd;
    }
    
    .ai-insight h4 {
        color: #5b21b6;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ============ INITIALIZE AI CLIENT ============
@st.cache_resource
def init_ai_client():
    """Initialize Anthropic client with API key"""
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        return anthropic.Anthropic(api_key=api_key)
    except:
        return None

client = init_ai_client()

# ============ AI FUNCTIONS ============
def get_ai_summary(project_title, project_description):
    """Get AI-powered summary of a project"""
    if not client:
        return None
    
    try:
        prompt = f"""Provide a brief, professional summary of this energy project in 2-3 sentences:
        
Project: {project_title}
Description: {project_description}

Focus on: project scale, energy type, strategic importance, and current status."""
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"✨ Energy project at {project_title[:50]}..."

def get_ai_insights(df):
    """Get AI-powered insights about the current data"""
    if not client or len(df) == 0:
        return None
    
    try:
        # Prepare summary for AI
        type_summary = df['energy_type'].value_counts().to_dict()
        county_summary = df['county'].value_counts().head(3).to_dict()
        recent = df.nlargest(3, 'date_parsed') if 'date_parsed' in df.columns else df.head(3)
        
        prompt = f"""As an Irish energy planning analyst, provide 3 key insights about these projects:
        
Energy Types: {type_summary}
Top Counties: {county_summary}
Total Projects: {len(df)}
Recent Projects: {', '.join(recent['title'].tolist()[:3])}

Provide insights about:
1. Trends in energy development
2. Geographic patterns
3. Notable observations

Keep response concise, under 100 words."""
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except:
        return None

# ============ HEADER ============
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<h1 class="gradient-header">⚡ GridWatch Ireland</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; color: #4b5563;">🇮🇪 Real-time Energy Planning Intelligence | Powered by AI</p>', unsafe_allow_html=True)
with col2:
    st.image("https://img.icons8.com/color/96/ireland.png", width=100)

st.markdown('<div class="animated-border"></div>', unsafe_allow_html=True)
st.markdown("")

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
    st.error("No data loaded. Please contact administrator.")
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
    min_date = valid_dates.min()
    max_date = valid_dates.max()
else:
    min_date = datetime.now() - timedelta(days=365)
    max_date = datetime.now()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.2rem; border-radius: 20px; color: white; margin-bottom: 1.5rem;">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯 AI-Powered</div>
        <div style="font-weight: 600;">Energy Intelligence</div>
        <div style="font-size: 0.8rem; opacity: 0.9; margin-top: 0.5rem;">Real-time insights & analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📅 Date Range")
    
    start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)
    
    st.markdown("**⚡ Quick Select:**")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("7d", use_container_width=True):
            start_date = max_date - timedelta(days=7)
            end_date = max_date
            st.rerun()
    with q2:
        if st.button("30d", use_container_width=True):
            start_date = max_date - timedelta(days=30)
            end_date = max_date
            st.rerun()
    with q3:
        if st.button("90d", use_container_width=True):
            start_date = max_date - timedelta(days=90)
            end_date = max_date
            st.rerun()
    
    show_recent = st.checkbox("📅 Last 30 days", value=True)
    if show_recent:
        start_date = max_date - timedelta(days=30)
        end_date = max_date
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    selected_type = st.selectbox("Energy Type", ["All"] + sorted(df['energy_type'].unique().tolist()))
    selected_county = st.selectbox("County", ["All"] + sorted(df['county'].unique().tolist()))
    selected_status = st.selectbox("Status", ["All"] + sorted(df['status'].unique().tolist()))
    
    st.markdown("---")
    st.caption(f"📊 {len(df)} total projects in database")

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
    st.metric("Total Projects", len(df_filtered), delta=None)
with m2:
    st.metric("🌬️ Wind", len(df_filtered[df_filtered['energy_type'] == 'wind']))
with m3:
    st.metric("☀️ Solar", len(df_filtered[df_filtered['energy_type'] == 'solar']))
with m4:
    st.metric("🔋 BESS", len(df_filtered[df_filtered['energy_type'] == 'bess']))
with m5:
    st.metric("⚡ Grid", len(df_filtered[df_filtered['energy_type'] == 'grid']))

# AI Insights Panel
if client and len(df_filtered) > 0:
    st.markdown("---")
    with st.spinner("🤖 AI is analyzing project data..."):
        insights = get_ai_insights(df_filtered)
    
    if insights:
        st.markdown(f"""
        <div class="ai-insight">
            <h4>🤖 AI-Powered Insights</h4>
            <p style="margin-top: 0.5rem;">{insights}</p>
        </div>
        """, unsafe_allow_html=True)

# Date range info
if len(df_filtered) > 0:
    st.markdown(f"""
    <div class="custom-info">
        📅 Showing <strong>{len(df_filtered)}</strong> projects from 
        <strong>{start_date.strftime('%d %B %Y')}</strong> to <strong>{end_date.strftime('%d %B %Y')}</strong>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No projects found in this date range.")

st.markdown("---")

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "📈 Analytics", "📋 Project Directory"])

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

# ============ TAB 1: MAP ============
with tab1:
    map_col1, map_col2 = st.columns([3, 1])
    
    with map_col1:
        m = folium.Map(location=[53.4129, -8.2439], zoom_start=7, control_scale=True)
        folium.TileLayer('CartoDB positron', name='Light').add_to(m)
        folium.TileLayer('OpenStreetMap', name='Street').add_to(m)
        folium.TileLayer('CartoDB dark_matter', name='Dark').add_to(m)
        
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
            
            # Get AI summary if available
            if client and random.random() < 0.3:  # Sample some projects
                ai_summary = get_ai_summary(row.get('title', ''), row.get('description', ''))
            else:
                ai_summary = None
            
            popup_html = f"""
            <div style="font-family: 'Inter', sans-serif; min-width: 300px; max-width: 350px;">
                <div style="background: {color}; padding: 14px; border-radius: 16px 16px 0 0; color: white;">
                    <div style="font-size: 18px; font-weight: 700;">{icon} {etype.title()}</div>
                </div>
                <div style="padding: 18px; background: white; border-radius: 0 0 16px 16px;">
                    <div style="font-weight: 700; font-size: 15px; margin-bottom: 12px;">{row.get('title', 'No Title')[:100]}</div>
                    <div style="font-size: 13px; color: #4b5563; margin-bottom: 8px;">
                        <div><strong>📋 Ref:</strong> {row.get('ref', 'N/A')}</div>
                        <div><strong>📍 County:</strong> {row.get('county', 'Unknown')}</div>
                        <div><strong>📅 Lodged:</strong> {row.get('date_lodged', 'N/A')}</div>
                    </div>
            """
            
            if ai_summary:
                popup_html += f"""
                    <div style="background: #f3f4f6; padding: 10px; border-radius: 12px; margin: 10px 0; font-size: 12px;">
                        <strong>🤖 AI Summary:</strong><br>
                        {ai_summary[:120]}...
                    </div>
                """
            
            popup_html += f"""
                    <a href="{row.get('source_url', '#')}" target="_blank" 
                       style="display: inline-block; margin-top: 10px; 
                              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 8px 16px; text-decoration: none; 
                              border-radius: 12px; font-weight: 500; font-size: 13px;">
                        🔗 View Details →
                    </a>
                </div>
            </div>
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"{icon} {row.get('title', '')[:50]}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(marker_cluster)
        
        folium.LayerControl().add_to(m)
        map_html = m._repr_html_()
        html(map_html, height=600, width=750)
    
    with map_col2:
        st.markdown("### 📍 Legend")
        for etype, color in energy_colors.items():
            count = len(df_filtered[df_filtered['energy_type'] == etype])
            icon = energy_icons.get(etype, "❓")
            if count > 0 or etype in ['wind', 'solar', 'bess', 'grid']:
                st.markdown(
                    f'<div style="display: flex; align-items: center; margin: 10px 0; padding: 6px; border-radius: 10px; transition: 0.2s;">'
                    f'<span style="display: inline-block; width: 16px; height: 16px; background: {color}; border-radius: 50%; margin-right: 12px;"></span>'
                    f'<span style="flex: 1;"><b>{icon} {etype.title()}</b></span>'
                    f'<span style="background: #f3f4f6; padding: 2px 8px; border-radius: 20px; font-size: 12px;">{count}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        st.markdown("### 💡 Map Tips")
        st.markdown("""
        - 🖱️ **Click markers** for project details
        - 🔍 **Zoom in/out** for better view
        - 🗺️ **Layer control** (top right) to change style
        - 📍 **Clusters** show multiple projects
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.markdown(f"**📍 Projects:** {len(df_filtered)}")
        st.markdown(f"**🏙️ Counties:** {df_filtered['county'].nunique()}")
        st.markdown(f"**⚡ Types:** {df_filtered['energy_type'].nunique()}")

# ============ TAB 2: ANALYTICS ============
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥧 Project Distribution")
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
    
    with col2:
        st.markdown("#### 📊 Top Counties")
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
                xaxis_title="Number of Projects",
                yaxis_title="County",
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'}
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
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#764ba2'),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)'
            )])
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Applications",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Status Overview")
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
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
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
            "ref": "Reference",
            "title": "Project Name",
            "county": "County",
            "energy_type": "Type",
            "status": "Status",
            "date_lodged": "Lodged Date",
        },
        height=500
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df_display.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, f"gridwatch_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv", use_container_width=True)
    with col2:
        json_str = df_display.to_json(orient='records', indent=2)
        st.download_button("📥 Download JSON", json_str, f"gridwatch_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json", use_container_width=True)

# ============ FOOTER ============
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: #6b7280; font-size: 12px; padding: 1rem;">
        <b>⚡ GridWatch Ireland</b> | Data from An Coimisiún Pleanála<br>
        {len(df_filtered)} projects • {start_date.strftime('%d %B %Y')} → {end_date.strftime('%d %B %Y')}<br>
        🤖 AI-powered insights | 🇮🇪 Powering Ireland's Energy Transition
    </div>
    """,
    unsafe_allow_html=True
)
