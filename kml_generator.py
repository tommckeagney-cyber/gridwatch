import json
import pandas as pd

print("🗺️ Generating KML for Google Earth...")
print()

# Load data
with open("data/cases.json", "r") as f:
    cases = json.load(f)

print(f"📊 Loaded {len(cases)} projects")

if not cases:
    print("⚠️ No projects to export")
    exit()

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

# Colors for energy types
energy_colors = {
    "wind": "ff4285f4", "solar": "fff4b842", "bess": "ff34a853",
    "grid": "ffaa46ff", "offshore": "ff1cb5e0", "biogas": "ffff7043",
    "other": "ff9e9e9e"
}

# Build KML
kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>GridWatch Ireland - Energy Projects</name>
    <open>1</open>
    <description>Real-time energy planning applications in Ireland. Updated weekly.</description>
'''

# Add styles
for etype, color in energy_colors.items():
    kml += f'''
    <Style id="style_{etype}">
        <IconStyle>
            <scale>1.2</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>
            </Icon>
        </IconStyle>
    </Style>
'''

# Add placemarks
for case in cases:
    lat = case.get("latitude")
    lon = case.get("longitude")
    
    if lat is None:
        county = case.get("county", "Unknown")
        if county in county_coords:
            lat, lon = county_coords[county]
        else:
            continue
    
    etype = case.get("energy_type", "other")
    title = case.get("title", "Unknown")[:80]
    ref = case.get("ref", "N/A")
    status = case.get("status", "Unknown")
    date_lodged = case.get("date_lodged", "Unknown")
    url = case.get("source_url", "#")
    
    kml += f'''
    <Placemark>
        <name>{title}</name>
        <styleUrl>#style_{etype}</styleUrl>
        <description>
            <![CDATA[
            <div style="font-family: Arial; max-width: 300px;">
                <b>{title}</b><br>
                <b>Ref:</b> {ref}<br>
                <b>Type:</b> {etype.upper()}<br>
                <b>Status:</b> {status}<br>
                <b>Lodged:</b> {date_lodged}<br>
                <a href="{url}" target="_blank">View Details →</a>
            </div>
            ]]>
        </description>
        <Point>
            <coordinates>{lon},{lat},0</coordinates>
        </Point>
    </Placemark>
'''

kml += '''
</Document>
</kml>'''

# Save KML
with open("data/gridwatch.kml", "w") as f:
    f.write(kml)

print(f"✅ KML created: data/gridwatch.kml")
print(f"   {len(cases)} projects exported")

# Also create CSV
df = pd.DataFrame(cases)
df.to_csv("data/gridwatch_export.csv", index=False)
print(f"✅ CSV created: data/gridwatch_export.csv")
