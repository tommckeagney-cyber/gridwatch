import json
import pandas as pd

# Load data
with open("data/cases.json", "r") as f:
    cases = json.load(f)

print(f"📊 Loaded {len(cases)} records")

# Create a simple KML
kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>GridWatch Ireland</name>
<Placemark>
<name>Test Project</name>
<description>Energy project in Ireland</description>
<Point>
<coordinates>-8.2439,53.4129,0</coordinates>
</Point>
</Placemark>
</Document>
</kml>'''

# Save KML
with open("data/gridwatch.kml", "w") as f:
    f.write(kml)

print("✅ KML created at data/gridwatch.kml")
