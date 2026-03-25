"""
Live Scraper for GridWatch Ireland
Fetches data for specific date ranges on demand
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

class LiveScraper:
    def __init__(self):
        self.base_url = "https://www.pleanala.ie"
        self.lists_url = f"{self.base_url}/en-ie/lists/cases"
        self.case_url = f"{self.base_url}/en-ie/case"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GridWatchIreland/2.0)',
            'Accept-Language': 'en-IE,en;q=0.9',
        })
        
        # County centroids for geocoding
        self.county_centroids = {
            "Carlow": (52.8377, -6.9298), "Cavan": (53.9908, -7.3606),
            "Clare": (52.8627, -9.0259), "Cork": (51.8985, -8.4756),
            "Donegal": (54.6549, -8.1109), "Dublin": (53.3498, -6.2603),
            "Galway": (53.2707, -9.0568), "Kerry": (52.1546, -9.5231),
            "Kildare": (53.1584, -6.9028), "Kilkenny": (52.6538, -7.2493),
            "Laois": (53.0000, -7.3000), "Leitrim": (54.0000, -8.0000),
            "Limerick": (52.6638, -8.6267), "Longford": (53.7277, -7.7997),
            "Louth": (53.9257, -6.4827), "Mayo": (53.8378, -9.4001),
            "Meath": (53.6046, -6.6567), "Monaghan": (54.2500, -7.0000),
            "Offaly": (53.1000, -7.5000), "Roscommon": (53.6291, -8.1868),
            "Sligo": (54.2693, -8.4693), "Tipperary": (52.6807, -7.8246),
            "Waterford": (52.2593, -7.1101), "Westmeath": (53.5000, -7.5000),
            "Wexford": (52.4798, -6.4576), "Wicklow": (52.9915, -6.3647),
        }
        
        # Energy keywords
        self.energy_keywords = {
            "wind": ['wind farm','wind turbine','wind energy','wind power','windfarm'],
            "solar": ['solar farm','solar pv','photovoltaic','solar panel','solar energy'],
            "bess": ['battery storage','battery energy storage','bess','grid-scale battery'],
            "grid": ['substation','grid connection','transmission line','overhead line','underground cable'],
            "offshore": ['offshore wind','floating wind','offshore energy','marine energy'],
            "biogas": ['anaerobic digestion','biomethane','biogas','biomass','bioenergy'],
        }
        
        self.counties = [
            "Carlow","Cavan","Clare","Cork","Donegal","Dublin","Galway","Kerry",
            "Kildare","Kilkenny","Laois","Leitrim","Limerick","Longford","Louth",
            "Mayo","Meath","Monaghan","Offaly","Roscommon","Sligo","Tipperary",
            "Waterford","Westmeath","Wexford","Wicklow"
        ]
    
    def get_all_fridays_between(self, start_date: datetime, end_date: datetime) -> List[str]:
        """Get all Friday dates between start and end"""
        fridays = []
        current = start_date
        
        # Find first Friday
        days_to_friday = (4 - current.weekday()) % 7
        current = current + timedelta(days=days_to_friday)
        
        while current <= end_date:
            fridays.append(current.strftime('%d/%m/%Y'))
            current += timedelta(weeks=1)
        
        return fridays
    
    def fetch_weekly_list(self, list_type: str, week: str) -> List[Dict]:
        """Fetch one weekly list"""
        try:
            time.sleep(1.5)  # Be polite
            response = self.session.get(
                self.lists_url,
                params={'list': list_type, 'week': week},
                timeout=20
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            cases = []
            blocks = soup.find_all(lambda tag: tag.name in ('div','article','li') and 
                                  re.search(r'\b[35]\d{5}\b|ABP-\d+', tag.get_text()))
            
            for block in blocks:
                case = self._parse_case(block, list_type, week)
                if case:
                    cases.append(case)
            
            return cases
        except Exception as e:
            print(f"Error fetching {list_type} for week {week}: {e}")
            return []
    
    def _parse_case(self, block, list_type: str, week: str) -> Dict:
        """Parse a case block"""
        text = block.get_text(' ', strip=True)
        
        # Extract reference
        m = re.search(r'\b([35]\d{5})\b|ABP-([\d-]+)', text)
        if not m:
            return None
        
        ref = m.group(1) or 'ABP-' + m.group(2)
        
        # Extract title
        h = block.find(['h2','h3','h4','strong','a'])
        title = h.get_text(strip=True) if h else text[:120]
        
        # Extract description
        desc_m = re.search(r'(?:Description|Cur s[ií]os)[:\s]+(.+?)(?:\n|Status|Date|$)', text, re.I|re.S)
        description = desc_m.group(1).strip()[:500] if desc_m else text[:300]
        
        # Extract county
        county = "Unknown"
        for c in self.counties:
            if re.search(rf'\b{c}\b', text, re.I):
                county = c
                break
        
        # Extract status
        st_m = re.search(r'(?:Status|Stádas)[:\s]+(.+?)(?:\n|Date|$)', text, re.I|re.S)
        status = st_m.group(1).strip()[:120] if st_m else "Unknown"
        
        # Extract date
        date_m = re.search(r'(?:Lodged|Dáta an taiscthe)[:\s]+(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})', text, re.I)
        date_lodged = date_m.group(1) if date_m else week
        
        # Extract flags
        eiar = bool(re.search(r'\bEIAR\b', text, re.I))
        nis = bool(re.search(r'\bNIS\b|\bNatura\b', text, re.I))
        
        # Build URL
        nr = re.search(r'\d{5,6}', ref)
        url = f"{self.case_url}/{nr.group()}" if nr else self.case_url
        
        # Classify energy type
        combined = (title + " " + description).lower()
        energy_type = "other"
        is_energy = False
        
        for etype, keywords in self.energy_keywords.items():
            if any(kw in combined for kw in keywords):
                is_energy = True
                energy_type = etype
                break
        
        if is_energy:
            # Get coordinates (using county centroid for now)
            lat, lon = self.county_centroids.get(county, (53.4129, -8.2439))
            
            return {
                "ref": ref,
                "title": title,
                "description": description,
                "county": county,
                "status": status,
                "date_lodged": date_lodged,
                "date_signed": None,
                "eiar": eiar,
                "nis": nis,
                "list_type": list_type,
                "source_url": url,
                "energy_type": energy_type,
                "is_energy": is_energy,
                "week_ending": week,
                "latitude": lat,
                "longitude": lon
            }
        
        return None
    
    def scrape_date_range(self, start_date: datetime, end_date: datetime, 
                          list_types: List[str] = None, 
                          progress_callback=None) -> List[Dict]:
        """Scrape all cases between start and end dates"""
        if list_types is None:
            list_types = ['N', 'D', 'I', 'J']
        
        # Get all Fridays in the date range
        fridays = self.get_all_fridays_between(start_date, end_date)
        
        if progress_callback:
            progress_callback(f"Found {len(fridays)} weeks to scrape...")
        
        all_cases = []
        seen_refs = set()
        total_weeks = len(fridays) * len(list_types)
        processed = 0
        
        for week in fridays:
            for list_type in list_types:
                processed += 1
                if progress_callback:
                    progress_callback(f"Scraping week {week} ({list_type})... {processed}/{total_weeks}")
                
                cases = self.fetch_weekly_list(list_type, week)
                for case in cases:
                    if case and case['ref'] not in seen_refs:
                        seen_refs.add(case['ref'])
                        all_cases.append(case)
        
        return all_cases
