import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta

print("🕷️ Starting scraper...")

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

# Energy keywords
energy_keywords = [
    "wind farm", "wind turbine", "solar farm", "photovoltaic", 
    "battery storage", "bess", "substation", "grid connection"
]

# Irish counties list
counties = ["Carlow","Cavan","Clare","Cork","Donegal","Dublin","Galway","Kerry",
    "Kildare","Kilkenny","Laois","Leitrim","Limerick","Longford","Louth",
    "Mayo","Meath","Monaghan","Offaly","Roscommon","Sligo","Tipperary",
    "Waterford","Westmeath","Wexford","Wicklow"]

# Get last 2 Fridays (for testing)
def get_fridays(n=2):
    today = datetime.today()
    days_back = (today.weekday() - 4) % 7
    friday = today - timedelta(days=days_back)
    return [(friday - timedelta(weeks=i)).strftime("%d/%m/%Y") for i in range(n)]

# Fetch one page
def fetch_page(week):
    url = "https://www.pleanala.ie/en-ie/lists/cases"
    params = {"list": "N", "week": week}
    
    try:
        time.sleep(1)
        r = requests.get(url, params=params, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        
        cases = []
        # Find all text with reference numbers
        text = soup.get_text()
        
        # Simple check for energy keywords
        if any(kw in text.lower() for kw in energy_keywords):
            print(f"  Found energy projects in week {week}")
            cases.append({"week": week, "found": True})
        
        return cases
    except Exception as e:
        print(f"  Error: {e}")
        return []

# Run scraper
all_cases = []
weeks = get_fridays(2)

for week in weeks:
    print(f"Checking week: {week}")
    cases = fetch_page(week)
    all_cases.extend(cases)

print(f"\n✅ Done. Found {len(all_cases)} weeks with energy projects")

# Save to file
with open("data/cases.json", "w") as f:
    json.dump(all_cases, f, indent=2)

print("💾 Saved to data/cases.json")
