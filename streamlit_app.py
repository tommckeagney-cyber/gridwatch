import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from folium import plugins
from streamlit.components.v1 import html
import requests

st.set_page_config(
    page_title="GridWatch Ireland",
    page_icon="⚡",
    layout="wide"
)

# ============ DARK THEME CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
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
        color: #94a3b8;
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
    
    [data-testid="stMetric"] {
        background: rgba(30, 30, 46, 0.9);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #60a5fa;
    }
    
    [data-testid="stMetric"] .stMetricValue {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(96, 165, 250, 0.4);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(30, 30, 46, 0.6);
        backdrop-filter: blur(10px);
        padding: 8px;
        border-radius: 60px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 40px;
        padding: 10px 28px;
        font-weight: 600;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        color: white;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    
    .custom-info {
        background: rgba(30, 30, 46, 0.9);
        border-left: 4px solid #60a5fa;
        padding: 16px 20px;
        border-radius: 16px;
        margin: 20px 0;
        color: #e2e8f0;
    }
    
    .ai-insight {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(167, 139, 250, 0.1) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }
    
    .ai-insight h4 {
        color: #a78bfa;
        font-weight: 700;
    }
    
    .footer {
        text-align: center;
        color: #475569;
        font-size: 12px;
        padding: 1rem;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============ DEEPSEEK AI FUNCTIONS ============
def get_deepseek_key():
    """Get DeepSeek API key from secrets"""
    try:
        return st.secrets.get("DEEPSEEK_API_KEY")
    except:
        return None

def call_deepseek(prompt):
    """Call DeepSeek API"""
    api_key = get_deepseek_key()
    if not api_key:
        return None
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.5
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return None

def get_ai_summary(title, description):
    """Get AI summary of project"""
    prompt = f"""Summarize this energy project in 1-2 sentences:

Project: {title}
Details: {description[:300]}

Summary:"""
    result = call_deepseek(prompt)
    return result if result else "Energy infrastructure project under review."

def verify_energy(title, description):
    """Verify if project is energy-related"""
    prompt = f"""Is this project related to energy infrastructure (wind, solar, battery storage, grid, substations, power lines)? Answer YES or NO only.

Project: {title}
Details: {description[:200]}"""
    result = call_deepseek(prompt)
    return "YES" in result.upper() if result else None

# ============ HEADER ============
st.markdown('<h1 class="gradient-header">⚡ GridWatch Ireland</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Energy Planning Intelligence</p>', unsafe_allow_html=True)
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
    st.error("No data loaded.")
    st.stop()

df = pd.DataFrame(cases)
df['energy_type'] = df['energy_type'].fillna('unknown')
df['county'] = df['county'].fillna('Unknown')
df['status'] = df['status'].fillna('Unknown')
df['title'] = df['title'].fillna('No Title')

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%d/%m/%Y')
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

has_deepseek = get_deepseek_key() is not None

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🎯 AI-Powered Dashboard")
    if has_deepseek:
        st.success("🤖 DeepSeek AI Active")
    else:
        st.info("🤖 Add DeepSeek API key to .streamlit/secrets.toml")
    
    st.markdown("---")
    st.markdown("### 📅 Date Range")
    
    start_date = st.date_input("From", value=default_start, min_value=data_min_date, max_value=data_max_date, format="DD/MM/YYYY")
    end_date = st.date_input("To", value=default_end, min_value=data_min_date, max_value=data_max_date, format="DD/MM/YYYY")
    
    st.markdown("**Quick:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("7d"): start_date, end_date = data_max_date - timedelta(days=7), data_max_date; st.rerun()
    with c2:
        if st.button("30d"): start_date, end_date = data_max_date - timedelta(days=30), data_max_date; st.rerun()
    with c3:
        if st.button("90d"): start_date, end_date = data_max_date - timedelta(days=90), data_max_date; st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    selected_type = st.selectbox("Type", ["All"] + sorted(df['energy_type'].unique().tolist()))
    selected_county = st.selectbox("County", ["All"] + sorted(df['county'].unique().tolist()))
    selected_status = st.selectbox("Status", ["All"] + sorted(df['status'].unique().tolist()))
    
    st.markdown("---")
    st.caption(f"📊 {len(df)} total projects")

# ============ APPLY FILTERS ============
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

df_filtered = df[(df['date_parsed'].notna()) & (df['date_parsed'] >= start_dt) & (df['date_parsed'] <= end_dt)]

if selected_type != "All":
    df_filtered = df_filtered[df_filtered['energy_type'] == selected_type]
if selected_county != "All":
    df_filtered = df_filtered[df_filtered['county'] == selected_county]
if selected_status != "All":
    df_filtered = df_filtered[df_filtered['status'] == selected_status]

df_filtered = df_filtered.sort_values('date_parsed', ascending=False)

# ============ STATS ============
st.subheader("📊 Key Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("Total", len(df_filtered))
with c2: st.metric("🌬️ Wind", len(df_filtered[df_filtered['energy_type'] == 'wind']))
with c3: st.metric("☀️ Solar", len(df_filtered[df_filtered['energy_type'] == 'solar']))
with c4: st.metric("🔋 BESS", len(df_filtered[df_filtered['energy_type'] == 'bess']))
with c5: st.metric("⚡ Grid", len(df_filtered[df_filtered['energy_type'] == 'grid']))

if len(df_filtered) > 0:
    st.markdown(f"""
    <div class="custom-info">
        📅 {len(df_filtered)} projects from {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============ MAP DATA ============
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
    "other": "#9ca3af", "unknown": "#6b7280"
}

energy_icons = {
    "wind": "🌬️", "solar": "☀️", "bess": "🔋", "grid": "⚡",
    "offshore": "🌊", "biogas": "♻️", "other": "🏭", "unknown": "❓"
}

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "📈 Analytics", "📋 Project Directory"])

# ============ TAB 1: MAP ============
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        m = folium.Map(location=[53.4129, -8.2439], zoom_start=7)
        folium.TileLayer('CartoDB dark_matter', name='Dark').add_to(m)
        folium.TileLayer('OpenStreetMap', name='Street').add_to(m)
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        ai_cache = {}
        
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
            
            title = row.get('title', 'No Title')
            ref = row.get('ref', 'N/A')
            county = row.get('county', 'Unknown')
            status = row.get('status', 'Unknown')
            date_lodged = row.get('date_lodged', 'N/A')
            url = row.get('source_url', '#')
            desc = row.get('description', '')
            
            ai_summary = None
            ai_verified = None
            
            if has_deepseek:
                cache_key = ref
                if cache_key not in ai_cache:
                    ai_cache[cache_key] = {
                        'summary': get_ai_summary(title, desc),
                        'verified': verify_energy(title, desc)
                    }
                ai_summary = ai_cache[cache_key]['summary']
                ai_verified = ai_cache[cache_key]['verified']
            
            popup = f"""
            <div style="min-width:280px; background:#1e1e2e; border-radius:12px; overflow:hidden;">
                <div style="background:{color}; padding:10px; color:white; font-weight:600;">{icon} {etype.upper()}</div>
                <div style="padding:12px;">
                    <b>{title[:80]}</b><br>
                    <small>📋 {ref} | 📍 {county} | {status} | 📅 {date_lodged}</small>
            """
            
            if ai_verified is not None:
                if ai_verified:
                    popup += '<div style="margin:8px 0;"><span style="background:#22c55e20; color:#22c55e; padding:2px 8px; border-radius:20px; font-size:11px;">✅ Energy Project Verified</span></div>'
                else:
                    popup += '<div style="margin:8px 0;"><span style="background:#ef444420; color:#ef4444; padding:2px 8px; border-radius:20px; font-size:11px;">⚠️ Not Energy-Related</span></div>'
            
            if ai_summary:
                popup += f'<div style="background:#60a5fa10; padding:8px; border-radius:8px; margin:8px 0;"><small>🤖 {ai_summary}</small></div>'
            
            popup += f'<a href="{url}" target="_blank" style="display:inline-block; margin-top:8px; background:#60a5fa; color:white; padding:4px 12px; border-radius:8px; text-decoration:none; font-size:12px;">🔗 View Details</a></div></div>'
            
            folium.CircleMarker(
                location=[lat, lon], radius=7, popup=folium.Popup(popup, max_width=380),
                tooltip=f"{icon} {title[:50]}", color=color, fill=True, fillColor=color, fillOpacity=0.7, weight=2
            ).add_to(marker_cluster)
        
        folium.LayerControl().add_to(m)
        html(m._repr_html_(), height=550, width=700)
    
    with col2:
        st.markdown("### 📍 Legend")
        for etype, color in energy_colors.items():
            count = len(df_filtered[df_filtered['energy_type'] == etype])
            icon = energy_icons.get(etype, "❓")
            st.markdown(f'<div><span style="display:inline-block; width:12px; height:12px; background:{color}; border-radius:50%;"></span> {icon} {etype.title()}: {count}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🤖 AI Features")
        if has_deepseek:
            st.markdown("- ✅ Click markers for AI summaries\n- 🔍 Energy verification badges\n- 💡 Smart project insights")
        else:
            st.markdown("Add DeepSeek API key to enable AI summaries and verification.")

# ============ TAB 2: ANALYTICS ============
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Projects by Type")
        type_counts = df_filtered['energy_type'].value_counts()
        if len(type_counts) > 0:
            fig = go.Figure(data=[go.Pie(labels=type_counts.index, values=type_counts.values, hole=0.4)])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Top Counties")
        county_counts = df_filtered['county'].value_counts().head(10)
        if len(county_counts) > 0:
            fig = go.Figure(data=[go.Bar(x=county_counts.values, y=county_counts.index, orientation='h')])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig, use_container_width=True)

# ============ TAB 3: PROJECT DIRECTORY ============
with tab3:
    search = st.text_input("🔍 Search", placeholder="Search by title, ref, or county...")
    df_display = df_filtered.copy()
    if search:
        mask = (df_display['title'].str.contains(search, case=False, na=False) |
                df_display['ref'].str.contains(search, case=False, na=False) |
                df_display['county'].str.contains(search, case=False, na=False))
        df_display = df_display[mask]
    
    st.dataframe(df_display[['ref', 'title', 'county', 'energy_type', 'status', 'date_lodged']], use_container_width=True)
    
    csv = df_display.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, f"gridwatch_{start_date.strftime('%Y%m%d')}.csv")

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    ⚡ GridWatch Ireland | Data from An Coimisiún Pleanála | Powered by DeepSeek AI
</div>
""", unsafe_allow_html=True)
