import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime, timedelta

print("🕷️ Starting GridWatch scraper...")
print()

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
ENERGY_KEYWORDS = {
    "wind": ["wind farm", "wind turbine", "wind energy", "wind power"],
    "solar": ["solar farm", "solar pv", "photovoltaic", "solar panel"],
    "bess": ["battery storage", "battery energy", "bess", "grid-scale battery"],
    "grid": ["substation", "grid connection", "transmission line"],
    "offshore": ["offshore wind", "marine energy"],
    "biogas": ["anaerobic digestion", "biomethane", "biogas"],
}

COUNTIES = ["Carlow","Cavan","Clare","Cork","Donegal","Dublin","Galway","Kerry",
    "Kildare","Kilkenny","Laois","Leitrim","Limerick","Longford","Louth",
    "Mayo","Meath","Monaghan","Offaly","Roscommon","Sligo","Tipperary",
    "Waterford","Westmeath","Wexford","Wicklow"]

BASE_URL = "https://www.pleanala.ie"
LISTS_URL = f"{BASE_URL}/en-ie/lists/cases"

def get_page(url, params=None):
    try:
        time.sleep(1.5)
        r = requests.get(url, params=params, headers={"User-Agent": "GridWatch/1.0"}, timeout=20)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  Request failed: {e}")
        return None

def last_n_fridays(n):
    today = datetime.today()
    days_back = (today.weekday() - 4) % 7
    friday = today - timedelta(days=days_back)
    return [(friday - timedelta(weeks=i)).strftime("%d/%m/%Y") for i in range(n)]

def fetch_weekly_list(list_type, week):
    soup = get_page(LISTS_URL, params={"list": list_type, "week": week})
    if not soup:
        return []
    
    cases = []
    blocks = soup.find_all(lambda tag: tag.name in ("div","article","li") and 
                          re.search(r"\b[35]\d{5}\b|ABP-\d+", tag.get_text()))
    
    for block in blocks:
        text = block.get_text(" ", strip=True)
        m = re.search(r"\b([35]\d{5})\b|ABP-([\d-]+)", text)
        if not m:
            continue
        
        ref = m.group(1) or "ABP-" + m.group(2)
        h = block.find(["h2","h3","h4","strong","a"])
        title = h.get_text(strip=True) if h else text[:120]
        
        desc_m = re.search(r"(?:Description|Cur s[ií]os)[:\s]+(.+?)(?:\n|Status|Date|$)", text, re.I|re.S)
        description = desc_m.group(1).strip()[:500] if desc_m else text[:300]
        
        county = "Unknown"
        for c in COUNTIES:
            if re.search(rf"\b{c}\b", text, re.I):
                county = c
                break
        
        st_m = re.search(r"(?:Status|Stádas)[:\s]+(.+?)(?:\n|Date|$)", text, re.I|re.S)
        status = st_m.group(1).strip()[:120] if st_m else "Unknown"
        
        date_m = re.search(r"(?:Lodged|Dáta an taiscthe)[:\s]+(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})", text, re.I)
        date_lodged = date_m.group(1) if date_m else week
        
        nr = re.search(r"\d{5,6}", ref)
        url = f"{BASE_URL}/en-ie/case/{nr.group()}" if nr else BASE_URL
        
        combined = (title + " " + description).lower()
        energy_type = "other"
        is_energy = False
        
        for etype, keywords in ENERGY_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                is_energy = True
                energy_type = etype
                break
        
        if is_energy:
            lat, lon = county_coords.get(county, [53.4129, -8.2439])
            
            cases.append({
                "ref": ref,
                "title": title,
                "description": description,
                "county": county,
                "status": status,
                "date_lodged": date_lodged,
                "date_signed": None,
                "list_type": list_type,
                "source_url": url,
                "energy_type": energy_type,
                "week_ending": week,
                "latitude": lat,
                "longitude": lon
            })
    
    return cases

print("🕷️ Starting scrape...")
print()

all_cases = []
seen_refs = set()
week_dates = last_n_fridays(4)

for week in week_dates:
    print(f"📅 Processing week: {week}")
    for ltype in ["N", "D", "I", "J"]:
        cases = fetch_weekly_list(ltype, week)
        for c in cases:
            if c["ref"] not in seen_refs:
                seen_refs.add(c["ref"])
                all_cases.append(c)

print()
print(f"✅ Found {len(all_cases)} energy cases")
print()

# Save to JSON
with open("data/cases.json", "w") as f:
    json.dump(all_cases, f, indent=2, default=str)

print("💾 Saved to data/cases.json")

# Summary
type_counts = {}
for c in all_cases:
    t = c.get("energy_type", "unknown")
    type_counts[t] = type_counts.get(t, 0) + 1

print("\n📊 Summary by type:")
for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"   {t}: {count}")

print("\n✅ Scraper finished!")
