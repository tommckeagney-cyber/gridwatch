"""
GIS Export for GridWatch Ireland
Generates GeoJSON and CSV files for QGIS
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_geojson(cases_file="data/cases.json", output_file="data/gridwatch.geojson"):
    """Generate GeoJSON file for QGIS"""
    
    # Load cases
    with open(cases_file, 'r') as f:
        cases = json.load(f)
    
    if not cases:
        print("No cases found")
        return
    
    # County centroids for fallback coordinates
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
    
    # Energy type colors for QGIS styling
    energy_styles = {
        "wind": {"color": "#3b82f6", "name": "Wind Farm"},
        "solar": {"color": "#eab308", "name": "Solar Farm"},
        "bess": {"color": "#22c55e", "name": "Battery Storage"},
        "grid": {"color": "#a855f7", "name": "Grid Infrastructure"},
        "offshore": {"color": "#06b6d4", "name": "Offshore Wind"},
        "biogas": {"color": "#f97316", "name": "Biogas"},
        "hydrogen": {"color": "#ec489a", "name": "Hydrogen"},
        "hydro": {"color": "#14b8a6", "name": "Hydroelectric"},
        "data_centre": {"color": "#6b7280", "name": "Data Centre"},
        "other": {"color": "#9ca3af", "name": "Other Energy"}
    }
    
    # Build GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "name": "GridWatch Ireland",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": []
    }
    
    for case in cases:
        # Get coordinates
        lat = case.get('latitude')
        lon = case.get('longitude')
        
        if lat is None or pd.isna(lat):
            county = case.get('county', 'Unknown')
            if county in county_coords:
                lat, lon = county_coords[county]
            else:
                continue
        
        etype = case.get('energy_type', 'other')
        style = energy_styles.get(etype, energy_styles['other'])
        
        # Create feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "ref": case.get('ref', 'N/A'),
                "title": case.get('title', 'Unknown')[:100],
                "county": case.get('county', 'Unknown'),
                "energy_type": etype,
                "energy_name": style['name'],
                "color": style['color'],
                "capacity_mw": case.get('capacity_mw', 0),
                "status": case.get('status', 'Unknown'),
                "date_lodged": case.get('date_lodged', 'Unknown'),
                "source_url": case.get('source_url', '#'),
                "description": case.get('description', '')[:200]
            }
        }
        geojson["features"].append(feature)
    
    # Save GeoJSON
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"✅ GeoJSON created: {output_file}")
    print(f"   {len(geojson['features'])} features")
    
    # Also create a simple CSV as backup
    df = pd.DataFrame([f["properties"] for f in geojson["features"]])
    df["longitude"] = [f["geometry"]["coordinates"][0] for f in geojson["features"]]
    df["latitude"] = [f["geometry"]["coordinates"][1] for f in geojson["features"]]
    df.to_csv("data/gridwatch_gis.csv", index=False)
    print(f"✅ CSV created: data/gridwatch_gis.csv")
    
    return geojson

if __name__ == "__main__":
    generate_geojson()
