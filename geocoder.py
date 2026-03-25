"""
Geocoder for Irish energy project locations
Converts addresses to coordinates using multiple free services
"""

import requests
import re
import time
import logging
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IrishGeocoder:
    """Find coordinates for Irish addresses"""
    
    # County centroids as fallback
    COUNTY_CENTROIDS = {
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
    
    # Irish town keywords to look for
    TOWN_PATTERNS = [
        r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "at Town Name"
        r'near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "near Town Name"
        r'land\s+at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "land at Town Name"
        r'site\s+at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "site at Town Name"
    ]
    
    def __init__(self, delay=0.5):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GridWatchIreland/1.0 (energy-planning-research)'
        })
    
    def extract_town(self, text: str) -> Optional[str]:
        """Extract town name from description"""
        text = text.lower()
        
        # Look for common patterns
        for pattern in self.TOWN_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Look for Irish town keywords
        common_towns = [
            "kilkenny", "cork", "dublin", "galway", "limerick", "waterford",
            "wexford", "wicklow", "kildare", "meath", "louth", "monaghan",
            "cavan", "leitrim", "roscommon", "sligo", "mayo", "kerry",
            "clare", "tipperary", "laois", "offaly", "westmeath", "longford"
        ]
        
        for town in common_towns:
            if town in text:
                return town.title()
        
        return None
    
    def geocode_town(self, town: str, county: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a town using OSM Nominatim"""
        query = f"{town}, {county}, Ireland"
        
        try:
            time.sleep(self.delay)
            response = self.session.get(
                'https://nominatim.openstreetmap.org/search',
                params={
                    'q': query,
                    'format': 'json',
                    'limit': 1,
                    'addressdetails': 0
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    logger.info(f"Found coordinates for {town}: {lat}, {lon}")
                    return (lat, lon)
            else:
                logger.warning(f"Geocoding failed for {query}: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error geocoding {query}: {e}")
        
        return None
    
    def extract_coordinates_from_text(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract coordinates directly from text if present"""
        # Look for Irish Grid coordinates (e.g., "E 123456, N 234567")
        irish_grid = re.search(r'E\s*(\d{5,6})\s*[, ]*\s*N\s*(\d{5,6})', text, re.I)
        if irish_grid:
            # Convert Irish Grid to lat/lon (simplified - would need proper conversion)
            # For now, return None and rely on town extraction
            pass
        
        # Look for decimal degrees
        lat_lon = re.search(r'(\d{1,3}\.\d+)\s*[, ]\s*(-?\d{1,3}\.\d+)', text)
        if lat_lon:
            try:
                lat = float(lat_lon.group(1))
                lon = float(lat_lon.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except:
                pass
        
        return None
    
    def geocode_project(self, title: str, description: str, county: str) -> Tuple[float, float]:
        """
        Find coordinates for a project
        Returns (lat, lon) - falls back to county centroid if nothing found
        """
        # Combine title and description
        full_text = f"{title} {description}"
        
        # Try to extract coordinates directly
        coords = self.extract_coordinates_from_text(full_text)
        if coords:
            return coords
        
        # Try to extract town name
        town = self.extract_town(full_text)
        if town:
            coords = self.geocode_town(town, county)
            if coords:
                return coords
        
        # Fall back to county centroid
        centroid = self.COUNTY_CENTROIDS.get(county, (53.4129, -8.2439))
        logger.info(f"Using county centroid for {county}: {centroid}")
        return centroid

# Test function
if __name__ == "__main__":
    geocoder = IrishGeocoder()
    
    # Test with sample projects
    test_cases = [
        ("Wind Farm", "Development of 5 turbines at Cloghan, Co. Donegal", "Donegal"),
        ("Solar Farm", "Land at Ballinaboola, Co. Wexford", "Wexford"),
        ("BESS", "Site at Coolattin, Co. Wicklow", "Wicklow"),
    ]
    
    for title, desc, county in test_cases:
        lat, lon = geocoder.geocode_project(title, desc, county)
        print(f"{title} - {county}: ({lat}, {lon})")
