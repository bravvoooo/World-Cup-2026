import os 
import time
import json
from datetime import datetime, timezone, timedelta
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

def _do_get(url, headers):
    """GET with timeout and network error logging. Re-raises on failure."""
    try:
        return requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"[error] Network request failed: {e}")
        raise

def _refresh_cache(ttl_seconds, endpoint_path, filename):
    data = _fetch_from_api(endpoint_path)
    info = {
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'ttl_seconds': ttl_seconds,
        'data': data
    }
    with open(filename, 'w') as file:
        json.dump(info, file)
    return data

def _fetch_from_api(endpoint_path: str):
    """Fetch data from the football-data.org API. Returns parsed JSON, or None on 404."""
    url = BASE_URL + "/" + endpoint_path
    headers = {"X-Auth-Token": API_KEY}
    response = _do_get(url, headers)
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        time.sleep(retry_after)
        response = _do_get(url, headers)
        if response.status_code == 429:
            raise requests.exceptions.HTTPError(f"429 after retry from {url}")
    if response.status_code == requests.codes.not_found:  # 404 means resource doesn't exist — caller decides UX, so return None
        return None
    response.raise_for_status()
    requests_available = int(response.headers.get("X-Requests-Available-Minute", 100000)) # missing header should not trigger sleep
    if requests_available <= 2: # Proactive throttle
        seconds_until_reset = int(response.headers.get("X-RequestCounter-Reset", 60))
        time.sleep(seconds_until_reset)
    return response.json()

def _get_with_cache(cache_key: str, ttl_seconds: int, endpoint_path: str):
    """Get data from cache if available and not expired, otherwise fetch from API and cache it."""
    folder_location = Path('data/cache')
    folder_location.mkdir(parents=True, exist_ok=True)
    filename = folder_location / f'{cache_key}.json'
    if not filename.exists():       # This is the cache MISS, if the data isn't there to grab, this will run
        return _refresh_cache(ttl_seconds, endpoint_path, filename)
    else:       # This is the cache HIT, it will return the already had data
        with open(filename) as file_handle:
            info = json.load(file_handle)
        fetched_at_str = info['fetched_at']
        ttl = info['ttl_seconds']
        payload = info['data']
        fetched_at = datetime.fromisoformat(fetched_at_str)
        age = datetime.now(timezone.utc) - fetched_at
        age_seconds = age.total_seconds()
        if age_seconds < ttl:
            return payload
        else:
            return _refresh_cache(ttl_seconds, endpoint_path, filename)

def get_competition():
    """Get the World Cup competition data"""
    return _get_with_cache(cache_key="competition_wc", ttl_seconds=86400, endpoint_path="competitions/WC")

def get_matches():
    """Get the matches for the World Cup"""
    response = _get_with_cache(cache_key="matches_wc", ttl_seconds=900, endpoint_path="competitions/WC/matches")
    return response['matches']
