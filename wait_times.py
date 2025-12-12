#!/usr/bin/env python3
"""
Efteling Wait Times Fetcher
Fetches live waiting times from Queue-Times.com API
Updates every 5 minutes during park hours
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Queue-Times.com API (free, requires attribution)
QUEUE_TIMES_API = "https://queue-times.com/parks/160/queue_times.json"
QUEUE_TIMES_ATTRIBUTION = "Powered by Queue-Times.com"
QUEUE_TIMES_URL = "https://queue-times.com/parks/160"

# Data storage
DATA_DIR = Path(os.environ.get("DATA_DIR", "/app/data"))
WAIT_TIMES_FILE = DATA_DIR / "wait_times.json"
ATTRACTIONS_FILE = DATA_DIR / "attractions.json"

# Name mapping: Queue-Times name -> Our attraction name
NAME_MAPPING = {
    "Baron 1898": "Baron 1898",
    "Python": "Python",
    "Joris en de Draak - Vuur": "Joris en de Draak",
    "Joris en de Draak - Water": "Joris en de Draak",
    "Vogel Rok": "Vogel Rok",
    "Max & Moritz": "Max & Moritz",
    "De Vliegende Hollander": "De Vliegende Hollander",
    "Piraña": "Piraña",
    "Gondoletta": "Gondoletta",
    "Symbolica": "Symbolica",
    "Droomvlucht": "Droomvlucht",
    "Fata Morgana": "Fata Morgana",
    "Carnaval Festival": "Carnaval Festival",
    "Villa Volta": "Villa Volta",
    "Halve Maen": "Halve Maen",
    "Pagode": "Pagode",
    "Stoomtrein": "Stoomtrein",
    "Monorail": "De Monorail",
    "De Oude Tufferbaan": "De Oude Tufferbaan",
    "Kinderspoor": "Kinderspoor",
    "Stoomcarrousel": "Stoomcarrousel",
    "Danse Macabre": "Danse Macabre",
    "Fabula": "Fabula",
    "Sirocco": "Sirocco",
    "Sprookjesbos": "Sprookjesbos",
    "Fairytale Forest": "Sprookjesbos",
    "Spookslot": "Spookslot",
    "Raveleijn": "Raveleijn",
    "Aquanura": "Aquanura",
}


def fetch_wait_times() -> Optional[dict]:
    """Fetch current wait times from Queue-Times.com API"""
    try:
        logger.info(f"Fetching wait times from {QUEUE_TIMES_API}")
        
        response = requests.get(
            QUEUE_TIMES_API,
            headers={"User-Agent": "Efteling-Height-Checker/1.0"},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the response
        wait_times = {}
        park_open = False
        
        for land in data.get("lands", []):
            for ride in land.get("rides", []):
                name = ride.get("name", "")
                mapped_name = NAME_MAPPING.get(name, name)
                
                wait_times[mapped_name] = {
                    "original_name": name,
                    "is_open": ride.get("is_open", False),
                    "wait_time": ride.get("wait_time", 0),
                    "last_updated": ride.get("last_updated"),
                }
                
                if ride.get("is_open"):
                    park_open = True
        
        # Also check rides not in lands
        for ride in data.get("rides", []):
            name = ride.get("name", "")
            mapped_name = NAME_MAPPING.get(name, name)
            
            wait_times[mapped_name] = {
                "original_name": name,
                "is_open": ride.get("is_open", False),
                "wait_time": ride.get("wait_time", 0),
                "last_updated": ride.get("last_updated"),
            }
            
            if ride.get("is_open"):
                park_open = True
        
        result = {
            "wait_times": wait_times,
            "park_open": park_open,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "source": QUEUE_TIMES_URL,
            "attribution": QUEUE_TIMES_ATTRIBUTION,
        }
        
        logger.info(f"Fetched wait times for {len(wait_times)} attractions")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch wait times: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse wait times response: {e}")
        return None


def save_wait_times(data: dict) -> None:
    """Save wait times to JSON file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(WAIT_TIMES_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved wait times to {WAIT_TIMES_FILE}")


def load_wait_times() -> Optional[dict]:
    """Load wait times from JSON file"""
    if WAIT_TIMES_FILE.exists():
        with open(WAIT_TIMES_FILE) as f:
            return json.load(f)
    return None


def categorize_by_height(attractions: list, height_cm: int) -> dict:
    """
    Categorize attractions by availability for a given height.
    (Duplicated from scraper.py for independence)
    """
    result = {'independent': [], 'with_companion': [], 'not_available': []}
    
    for attr in attractions:
        min_h = attr.get("min_height_cm")
        supervision_h = attr.get("supervision_height_cm")
        
        if min_h is None and supervision_h is None:
            result['independent'].append(attr)
        elif min_h is None and supervision_h is not None:
            if height_cm >= supervision_h:
                result['independent'].append(attr)
            else:
                result['with_companion'].append(attr)
        elif min_h is not None:
            if height_cm >= min_h:
                result['independent'].append(attr)
            elif supervision_h is not None and height_cm >= supervision_h:
                result['with_companion'].append(attr)
            else:
                result['not_available'].append(attr)
    
    return result


def merge_wait_times_with_attractions() -> None:
    """Merge wait times into the main attractions data and regenerate height categories"""
    if not ATTRACTIONS_FILE.exists():
        logger.warning("Attractions file not found, skipping merge")
        return
    
    wait_data = load_wait_times()
    if not wait_data:
        logger.warning("No wait times data to merge")
        return
    
    with open(ATTRACTIONS_FILE) as f:
        attractions_data = json.load(f)
    
    wait_times = wait_data.get("wait_times", {})
    
    # Add wait times to each attraction
    for attr in attractions_data.get("attractions", []):
        name = attr.get("name")
        if name in wait_times:
            wt = wait_times[name]
            attr["is_open"] = wt.get("is_open", False)
            attr["wait_time"] = wt.get("wait_time", 0) if wt.get("is_open") else None
            attr["wait_last_updated"] = wt.get("last_updated")
        else:
            attr["is_open"] = None  # Unknown
            attr["wait_time"] = None
            attr["wait_last_updated"] = None
    
    # IMPORTANT: Regenerate height_categories with updated attraction data (including wait times)
    attractions_list = attractions_data.get("attractions", [])
    attractions_data["height_categories"] = {
        str(h): categorize_by_height(attractions_list, h) 
        for h in [95, 100, 110, 120, 130, 135, 140]
    }
    
    # Add wait time metadata
    attractions_data["wait_times_info"] = {
        "fetched_at": wait_data.get("fetched_at"),
        "park_open": wait_data.get("park_open"),
        "source": wait_data.get("source"),
        "attribution": wait_data.get("attribution"),
    }
    
    with open(ATTRACTIONS_FILE, 'w') as f:
        json.dump(attractions_data, f, indent=2)
    
    logger.info("Merged wait times with attractions data and regenerated height categories")


def main():
    """Main function to fetch and save wait times"""
    logger.info("Starting wait times fetcher")
    
    data = fetch_wait_times()
    
    if data:
        save_wait_times(data)
        merge_wait_times_with_attractions()
        
        # Print summary
        wait_times = data.get("wait_times", {})
        open_rides = [name for name, wt in wait_times.items() if wt.get("is_open")]
        
        if open_rides:
            print(f"\n🎢 Park is OPEN - {len(open_rides)} attractions operating")
            print("\nCurrent wait times:")
            for name in sorted(open_rides):
                wt = wait_times[name]
                print(f"  {name}: {wt['wait_time']} min")
        else:
            print("\n🌙 Park is CLOSED")
    else:
        print("❌ Failed to fetch wait times")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
