""")

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

# AI Status
if deepseek_configured:
st.markdown("""
<div class="ai-insight">
<h4>🤖 DeepSeek AI Active</h4>
<p>Click on any map marker to see AI-powered project summaries and verification.</p>
</div>
""", unsafe_allow_html=True)
else:
st.markdown("""
<div class="custom-info">
🤖 <strong>DeepSeek AI Ready!</strong> Add your API key to enable:
<ul style="margin-top: 8px; margin-left: 20px;">
    <li>📝 AI-powered project summaries</li>
    <li>✅ Energy relevance verification</li>
    <li>🔍 Smart project insights</li>
</ul>
</div>
""", unsafe_allow_html=True)

if len(df_filtered) > 0:
st.markdown(f"""
<div class="custom-info">
📅 Showing <strong>{len(df_filtered)}</strong> projects lodged between 
<strong>{start_date.strftime('%d/%m/%Y')}</strong> and <strong>{end_date.strftime('%d/%m/%Y')}</strong>
</div>
""", unsafe_allow_html=True)

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
m = folium.Map(location=[53.4129, -8.2439], zoom_start=7, control_scale=True)
folium.TileLayer('CartoDB dark_matter', name='Dark').add_to(m)
folium.TileLayer('OpenStreetMap', name='Street').add_to(m)

marker_cluster = plugins.MarkerCluster(name='Projects').add_to(m)

# Create a list to store AI results (for caching)
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
    description = row.get('description', '')
    
    # Get AI summary if available
    ai_summary = None
    ai_verified = None
    
    if deepseek_configured:
        cache_key = ref
        if cache_key not in ai_cache:
            ai_cache[cache_key] = {
                'summary': get_ai_summary(title, description),
                'verified': verify_energy_relevance(title, description)
            }
        
        ai_summary = ai_cache[cache_key]['summary']
        ai_verified = ai_cache[cache_key]['verified']
    
    popup_html = f"""
    <div style="font-family: 'Inter', sans-serif; min-width: 300px; background: #1e1e2e; border-radius: 16px; overflow: hidden;">
        <div style="background: {color}; padding: 12px; color: white;">
            <div style="font-size: 16px; font-weight: 600;">{icon} {etype.title()}</div>
        </div>
        <div style="padding: 16px;">
            <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 8px;">{title[:100]}</div>
            <div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">
                <div><strong>Ref:</strong> {ref}</div>
                <div><strong>County:</strong> {county}</div>
                <div><strong>Status:</strong> {status}</div>
                <div><strong>Lodged:</strong> {date_lodged}</div>
            </div>
    """
    
    if ai_verified is not None:
        if ai_verified:
            popup_html += f'<div style="margin: 8px 0;"><span style="background: #22c55e20; color: #22c55e; padding: 2px 8px; border-radius: 20px; font-size: 11px;">✅ AI: Energy Project Verified</span></div>'
        else:
            popup_html += f'<div style="margin: 8px 0;"><span style="background: #ef444420; color: #ef4444; padding: 2px 8px; border-radius: 20px; font-size: 11px;">⚠️ AI: May not be energy-related</span></div>'
    
    if ai_summary:
        popup_html += f"""
            <div style="background: rgba(96, 165, 250, 0.1); padding: 12px; border-radius: 8px; margin: 10px 0; border-left: 3px solid {color};">
                <div style="font-size: 11px; color: #a78bfa; margin-bottom: 4px;">🤖 AI Summary</div>
                <div style="font-size: 12px; color: #cbd5e1;">{ai_summary}</div>
            </div>
        """
    
    popup_html += f"""
            <a href="{url}" target="_blank" 
               style="display: inline-block; margin-top: 8px; 
                      background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); 
                      color: white; padding: 6px 12px; text-decoration: none; 
                      border-radius: 8px; font-size: 12px;">
                🔗 View on pleanala.ie →
            </a>
        </div>
    </div>
    """
    
    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        popup=folium.Popup(popup_html, max_width=380),
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
st.markdown("### 🤖 AI Features")
if deepseek_configured:
    st.markdown("""
    - **📝 AI Summary:** Click any marker for project summary
    - **✅ Energy Verification:** AI checks if it's energy-related
    - **💡 Smart Insights:** Understand project scope quickly
    """)
else:
    st.markdown("""
    **Add DeepSeek API key to enable:**
    - AI project summaries
    - Energy relevance verification
    - Smart insights on map markers
    """)

st.markdown("---")
st.markdown("### 💡 Tips")
st.markdown("""
- 🖱️ **Click markers** for AI summaries
- ✅ **Verified badges** show energy relevance
- 🔍 **Zoom in/out** for better view
- 🗺️ **Layer control** (top right) to change map style
""")

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
        textfont=dict(color='#e2e8f0')
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        font=dict(color='#e2e8f0')
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
        textposition='outside'
    )])
    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis_title="Number of Projects",
        yaxis_title="County"
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
height=400
)

csv = df_display.to_csv(index=False)
st.download_button("📥 Download CSV", csv, f"gridwatch_{start_date.strftime('%Y%m%d')}.csv")

# ============ FOOTER ============
st.markdown("""
<div class="footer">
⚡ GridWatch Ireland | Data from An Coimisiún Pleanála | Powered by DeepSeek AI
</div>
""", unsafe_allow_html=True)
