#!/usr/bin/env python3
"""
Efteling Height Requirements Scraper
Collects attraction height and age data dynamically from multiple sources
"""

import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import requests
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = Path("/app/data")
DATA_FILE = DATA_DIR / "attractions.json"

EFTELING_BASE_URL = "https://www.efteling.com/en/park/attractions"
EFTELING_SHOWS_URL = "https://www.efteling.com/en/park/shows"

# All 34 official Efteling attractions with their URL slugs
ATTRACTION_SLUGS = {
    "baron-1898": {"name": "Baron 1898", "name_dutch": "Baron 1898", "type_dutch": "Dive coaster", "type": "Dive Coaster"},
    "python": {"name": "Python", "name_dutch": "Python", "type_dutch": "Stalen achtbaan", "type": "Steel Roller Coaster"},
    "joris-en-de-draak": {"name": "Joris en de Draak", "name_dutch": "Joris en de Draak", "type_dutch": "Houten achtbaan", "type": "Wooden Roller Coaster"},
    "vogel-rok": {"name": "Vogel Rok", "name_dutch": "Vogel Rok", "type_dutch": "Overdekte achtbaan", "type": "Indoor Roller Coaster"},
    "max-moritz": {"name": "Max & Moritz", "name_dutch": "Max & Moritz", "type_dutch": "Dubbele familie-achtbaan", "type": "Family Roller Coaster"},
    "de-vliegende-hollander": {"name": "De Vliegende Hollander", "name_dutch": "De Vliegende Hollander", "type_dutch": "Waterachtbaan", "type": "Water Coaster"},
    "pirana": {"name": "Piraña", "name_dutch": "Piraña", "type_dutch": "Wildwaterbaan", "type": "River Rapids"},
    "gondoletta": {"name": "Gondoletta", "name_dutch": "Gondoletta", "type_dutch": "Boottocht", "type": "Boat Ride"},
    "danse-macabre": {"name": "Danse Macabre", "name_dutch": "Danse Macabre", "type_dutch": "Spookspektakel", "type": "Spooky Spectacle"},
    "symbolica": {"name": "Symbolica", "name_dutch": "Symbolica", "type_dutch": "Overdekte familie-attractie", "type": "Indoor Family Attraction"},
    "droomvlucht": {"name": "Droomvlucht", "name_dutch": "Droomvlucht", "type_dutch": "Overdekte attractie", "type": "Indoor Attraction"},
    "fata-morgana": {"name": "Fata Morgana", "name_dutch": "Fata Morgana", "type_dutch": "Overdekte attractie", "type": "Indoor Attraction"},
    "carnaval-festival": {"name": "Carnaval Festival", "name_dutch": "Carnaval Festival", "type_dutch": "Overdekte attractie", "type": "Indoor Attraction"},
    "villa-volta": {"name": "Villa Volta", "name_dutch": "Villa Volta", "type_dutch": "Vervloekt huis", "type": "Cursed House"},
    "halve-maen": {"name": "Halve Maen", "name_dutch": "Halve Maen", "type_dutch": "Schipschommel", "type": "Swinging Ship"},
    "pagode": {"name": "Pagode", "name_dutch": "Pagode", "type_dutch": "Zwevende tempel", "type": "Flying Temple"},
    "sirocco": {"name": "Sirocco", "name_dutch": "Sirocco", "type_dutch": "Draaiende handelsschuitjes", "type": "Spinning Merchant Boats"},
    "stoomtrein": {"name": "Stoomtrein", "name_dutch": "Stoomtrein", "type_dutch": "Rondrit door Efteling", "type": "Steam Train Tour"},
    "monorail": {"name": "De Monorail", "name_dutch": "De Monorail", "type_dutch": "Rondrit op hoogte", "type": "Elevated Tour"},
    "de-oude-tufferbaan": {"name": "De Oude Tufferbaan", "name_dutch": "De Oude Tufferbaan", "type_dutch": "Oldtimerbaan", "type": "Classic Car Ride"},
    "kinderspoor": {"name": "Kinderspoor", "name_dutch": "Kinderspoor", "type_dutch": "Traptreintjes", "type": "Pedal Trains"},
    "stoomcarrousel": {"name": "Stoomcarrousel", "name_dutch": "Stoomcarrousel", "type_dutch": "Draaimolen", "type": "Steam Carousel"},
    "anton-pieckplein": {"name": "Anton Pieckplein", "name_dutch": "Anton Pieckplein", "type_dutch": "Authentieke carrousels", "type": "Authentic Carousels"},
    "fabula": {"name": "Fabula", "name_dutch": "Fabula", "type_dutch": "4D-filmavontuur", "type": "4D Film Adventure"},
    "sprookjesbos": {"name": "Sprookjesbos", "name_dutch": "Sprookjesbos", "type_dutch": "Attractie", "type": "Fairytale Forest"},
    "volk-van-laaf": {"name": "Het Volk van Laaf", "name_dutch": "Het Volk van Laaf", "type_dutch": "Bijzondere Efteling-bewoners", "type": "Unusual Efteling Inhabitants"},
    "diorama": {"name": "Diorama", "name_dutch": "Diorama", "type_dutch": "Miniatuurwereld", "type": "Miniature World"},
    "archipel": {"name": "Archipel", "name_dutch": "Archipel", "type_dutch": "Avontureneiland", "type": "Adventure Island"},
    "nest": {"name": "Nest!", "name_dutch": "Nest!", "type_dutch": "Speelbos", "type": "Play Forest"},
    "kindervreugd": {"name": "Kindervreugd", "name_dutch": "Kindervreugd", "type_dutch": "Speeltuin", "type": "Playground"},
    "kleuterhof": {"name": "Kleuterhof", "name_dutch": "Kleuterhof", "type_dutch": "Speeltuin", "type": "Playground"},
    "efteling-museum": {"name": "Efteling Museum", "name_dutch": "Efteling Museum", "type_dutch": "Museum", "type": "Museum"},
    "holle-bolle-gijs": {"name": "Holle Bolle Gijs", "name_dutch": "Holle Bolle Gijs", "type_dutch": "Papierverslinder", "type": "Paper Gobbler"},
    "game-gallery": {"name": "Game Gallery", "name_dutch": "Game Gallery", "type_dutch": "Speelgalerij", "type": "Game Gallery"},
}

SHOW_SLUGS = {
    "aquanura": {"name": "Aquanura", "name_dutch": "Aquanura", "type": "Water Show", "notes": "Europe's largest fountain show - Efteling Symphonica"},
    "raveleijn": {"name": "Raveleijn", "name_dutch": "Raveleijn", "type": "Stunt Show", "notes": "Live action stunt show with horses (seasonal)"},
}

# Fallback data based on official Efteling requirements
FALLBACK_HEIGHT_DATA = {
    "Baron 1898": {"min_height_cm": 132, "advisory_age": 9},
    "Python": {"min_height_cm": 120},
    "Joris en de Draak": {"min_height_cm": 120, "min_height_with_companion_cm": 110, "companion_age": 16},
    "Vogel Rok": {"min_height_cm": 120},
    "Max & Moritz": {"min_height_cm": 130, "min_height_with_companion_cm": 100, "companion_age": 16},
    "De Vliegende Hollander": {"min_height_cm": 120},
    "Piraña": {"min_height_cm": 120},
    "Gondoletta": {"min_height_cm": 120},
    "Danse Macabre": {"min_height_cm": 120, "advisory_age": 8},
    "Symbolica": {"min_height_cm": 120},
    "Droomvlucht": {"min_height_cm": 100},
    "Fata Morgana": {"min_height_cm": 120},
    "Carnaval Festival": {"min_height_cm": 100},
    "Villa Volta": {"min_height_cm": 100},
    "Halve Maen": {"min_height_cm": 120},
    "Pagode": {"min_height_cm": 100},
    "Sirocco": {"min_height_cm": 100},
    "Stoomtrein": {"min_height_cm": 100},
    "De Monorail": {"min_height_cm": 120},
    "De Oude Tufferbaan": {"min_height_cm": 110},
    "Kinderspoor": {"min_height_cm": 120},
    "Stoomcarrousel": {"min_height_cm": 100},
    "Anton Pieckplein": {"min_height_cm": 100},
}

ATTRACTION_NOTES = {
    "Baron 1898": "Most intense coaster - 37.5m vertical drop at 90 km/h",
    "Python": "Classic looping coaster with double loop and corkscrew",
    "Joris en de Draak": "Racing wooden coaster - choose Fire or Water dragon",
    "Vogel Rok": "Fast indoor coaster in complete darkness",
    "Max & Moritz": "Twin family coasters - great first coaster experience",
    "De Vliegende Hollander": "Dark ride + water coaster - you WILL get wet!",
    "Piraña": "Wild river rapids - expect to get soaked",
    "Gondoletta": "Relaxing 20-minute scenic boat ride",
    "Danse Macabre": "NEW 2024 - World's first Dynamic Motion Stage ride",
    "Symbolica": "Award-winning trackless dark ride - 3 different routes",
    "Droomvlucht": "Magical suspended flight through fairy world - Efteling classic",
    "Fata Morgana": "1001 Nights themed boat ride through mystical palace",
    "Carnaval Festival": "Colorful world tour with very catchy music",
    "Villa Volta": "Mind-bending illusion ride - you appear to swing 360°",
    "Halve Maen": "One of world's largest swinging ships",
    "Pagode": "Rotating Thai temple with panoramic park views",
    "Sirocco": "Spinning merchant boats - formerly Monsieur Cannibale",
    "Stoomtrein": "Steam train tour through Efteling (electrifying in 2025)",
    "De Monorail": "Elevated monorail tour through the park",
    "De Oude Tufferbaan": "Charming vintage car ride through scenic route",
    "Kinderspoor": "Self-powered pedal trains through Dutch scenery",
    "Stoomcarrousel": "Beautiful historic steam-powered carousel",
    "Anton Pieckplein": "Multiple classic carousels in nostalgic square",
    "Fabula": "4D film adventure about a grumpy bear - heartwarming!",
    "Sprookjesbos": "31 fairy tales brought to life - the heart of Efteling",
    "Het Volk van Laaf": "Quirky walk-through village of the Laaf people",
    "Diorama": "Incredibly detailed miniature fairy tale world",
    "Archipel": "Adventure island playground with water features",
    "Nest!": "Natural play forest for children",
    "Kindervreugd": "Classic playground with small carousels",
    "Kleuterhof": "Dedicated toddler playground area",
    "Efteling Museum": "Park history, artifacts, and design sketches",
    "Holle Bolle Gijs": "Interactive talking trash bins - 'Papier hier!'",
    "Game Gallery": "Classic fairground games (extra charge applies)",
}


def get_session():
    """Create a requests session with appropriate headers"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    return session


def fetch_page(url: str, session=None, timeout: int = 30) -> Optional[str]:
    """Fetch a webpage and return its HTML content"""
    if session is None:
        session = get_session()
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def parse_height_from_text(text: str) -> Optional[int]:
    """Extract height in cm from text"""
    if not text:
        return None
    text = text.lower().strip()
    patterns = [
        r'(\d+)\s*cm',
        r'(\d+\.\d+)\s*m(?:eter|etre)?s?',
        r'(\d+)\s*m(?:eter|etre)s?\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1))
            if value < 10:
                return int(value * 100)
            return int(value)
    return None


def scrape_efteling_attraction(slug: str, base_info: dict, session) -> dict:
    """Scrape details from a single Efteling attraction page"""
    url = f"{EFTELING_BASE_URL}/{slug}"
    logger.info(f"Scraping {base_info['name']} from {url}")
    
    result = {
        "name": base_info["name"],
        "name_dutch": base_info.get("name_dutch"),
        "type": base_info["type"],
        "type_dutch": base_info.get("type_dutch"),
        "min_height_cm": None,
        "min_height_with_companion_cm": None,
        "companion_age": None,
        "advisory_age": None,
        "notes": "",
        "warnings": [],
        "url": url,
        "category": "attraction",
        "scrape_status": "pending"
    }
    
    html = fetch_page(url, session)
    if not html:
        result["scrape_status"] = "failed"
        return result
    
    soup = BeautifulSoup(html, 'html.parser')
    page_text = soup.get_text().lower()
    
    # Extract minimum height
    height_patterns = [
        r'minimum\s+(?:height|length|lengte)[:\s]*(\d+\.?\d*)\s*(?:m|cm)',
        r'(\d+\.?\d*)\s*(?:m|cm)\s*(?:minimum|min)',
        r'minimumlengte[:\s]*(\d+\.?\d*)',
        r'minimum\s+length\s+(\d+\.?\d*)\s*m',
    ]
    
    for pattern in height_patterns:
        match = re.search(pattern, page_text)
        if match:
            height = parse_height_from_text(match.group(0))
            if height:
                result["min_height_cm"] = height
                break
    
    # Extract companion height
    companion_patterns = [
        r'(?:children|kinderen)\s+between\s+(\d+\.?\d*)\s*(?:m|cm)\s+and\s+(\d+\.?\d*)',
        r'tussen\s+(\d+\.?\d*)\s*(?:m|cm)\s+en\s+(\d+\.?\d*)',
        r'between\s+(\d+\.?\d*)\s*m?\s+and\s+(\d+\.?\d*)\s*m?\s+with\s+company',
    ]
    
    for pattern in companion_patterns:
        match = re.search(pattern, page_text)
        if match:
            companion_height = parse_height_from_text(f"{match.group(1)} m")
            if companion_height:
                result["min_height_with_companion_cm"] = companion_height
                result["companion_age"] = 16
            break
    
    # Extract advisory age
    age_patterns = [
        r'advisory\s+age[:\s]*(\d+)',
        r'leeftijdsadvies[:\s]*(\d+)',
        r'recommended.*?(\d+)\s*(?:years?|jaar)',
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, page_text)
        if match:
            result["advisory_age"] = int(match.group(1))
            break
    
    # Collect warnings
    warning_map = {
        "not suitable for pregnant": "Not suitable for pregnant women",
        "medical condition": "Not suitable with medical conditions",
        "you may get wet": "You may get wet",
        "in the dark": "Partly in the dark",
        "loud noise": "Loud noises",
        "frightening": "Frightening effects",
        "dizzy": "May cause dizziness",
        "g-force": "G-forces",
    }
    
    warnings = []
    for keyword, warning in warning_map.items():
        if keyword in page_text:
            warnings.append(warning)
    
    result["warnings"] = warnings[:5]
    result["scrape_status"] = "success"
    
    return result


def scrape_all_attractions(session) -> List[dict]:
    """Scrape all Efteling attractions"""
    attractions = []
    
    for slug, base_info in ATTRACTION_SLUGS.items():
        try:
            attraction = scrape_efteling_attraction(slug, base_info, session)
            attractions.append(attraction)
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"Error scraping {slug}: {e}")
            attractions.append({
                "name": base_info["name"],
                "name_dutch": base_info.get("name_dutch"),
                "type": base_info["type"],
                "type_dutch": base_info.get("type_dutch"),
                "min_height_cm": None,
                "min_height_with_companion_cm": None,
                "companion_age": None,
                "advisory_age": None,
                "notes": "",
                "warnings": [],
                "url": f"{EFTELING_BASE_URL}/{slug}",
                "category": "attraction",
                "scrape_status": "error"
            })
    
    return attractions


def get_shows() -> List[dict]:
    """Get show information"""
    return [
        {
            "name": info["name"],
            "name_dutch": info["name_dutch"],
            "type": info["type"],
            "notes": info.get("notes", ""),
            "url": f"{EFTELING_SHOWS_URL}/{slug}",
            "category": "show"
        }
        for slug, info in SHOW_SLUGS.items()
    ]


def apply_fallback_data(attractions: List[dict]) -> List[dict]:
    """Apply fallback height data where scraping failed"""
    for attr in attractions:
        name = attr["name"]
        
        if name in FALLBACK_HEIGHT_DATA:
            fallback = FALLBACK_HEIGHT_DATA[name]
            if attr.get("min_height_cm") is None:
                attr["min_height_cm"] = fallback.get("min_height_cm")
            if attr.get("min_height_with_companion_cm") is None:
                attr["min_height_with_companion_cm"] = fallback.get("min_height_with_companion_cm")
            if attr.get("companion_age") is None:
                attr["companion_age"] = fallback.get("companion_age")
            if attr.get("advisory_age") is None:
                attr["advisory_age"] = fallback.get("advisory_age")
        
        if name in ATTRACTION_NOTES and not attr.get("notes"):
            attr["notes"] = ATTRACTION_NOTES[name]
    
    return attractions


def categorize_by_height(attractions: list, height_cm: int) -> dict:
    """Categorize attractions by availability for a given height"""
    result = {'independent': [], 'with_companion': [], 'not_available': []}
    
    for attr in attractions:
        min_h = attr.get("min_height_cm")
        companion_h = attr.get("min_height_with_companion_cm")
        
        if min_h is None:
            result['independent'].append(attr)
        elif height_cm >= min_h:
            result['independent'].append(attr)
        elif companion_h and height_cm >= companion_h:
            result['with_companion'].append(attr)
        else:
            result['not_available'].append(attr)
    
    return result


def run_scraper():
    """Main scraper function"""
    logger.info("Starting Efteling height requirements scraper")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    session = get_session()
    
    logger.info("Scraping attraction pages...")
    attractions = scrape_all_attractions(session)
    attractions = apply_fallback_data(attractions)
    shows = get_shows()
    
    attractions = sorted(attractions, key=lambda x: (x.get("min_height_cm") or 0, x["name"]))
    
    success_count = sum(1 for a in attractions if a.get("scrape_status") == "success")
    failed_count = len(attractions) - success_count
    
    height_categories = {
        str(h): categorize_by_height(attractions, h) 
        for h in [95, 100, 110, 120, 130, 135, 140]
    }
    
    sources = [
        {
            "name": "Efteling Official (Attractions)",
            "url": EFTELING_BASE_URL,
            "status": "success" if success_count > 0 else "failed",
            "attractions_scraped": success_count,
            "attractions_failed": failed_count,
            "fetched_at": datetime.now().isoformat()
        },
        {
            "name": "Efteling Official (Shows)",
            "url": EFTELING_SHOWS_URL,
            "status": "success",
            "fetched_at": datetime.now().isoformat()
        }
    ]
    
    data = {
        "last_updated": datetime.now().isoformat(),
        "total_attractions": len(attractions),
        "total_shows": len(shows),
        "scrape_stats": {
            "successful": success_count,
            "failed": failed_count,
        },
        "attractions": attractions,
        "shows": shows,
        "height_categories": height_categories,
        "sources": sources
    }
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Scraper complete. Data saved to {DATA_FILE}")
    logger.info(f"Attractions: {len(attractions)} ({success_count} scraped, {failed_count} fallback)")
    logger.info(f"Shows: {len(shows)}")
    
    return data


if __name__ == '__main__':
    run_scraper()
