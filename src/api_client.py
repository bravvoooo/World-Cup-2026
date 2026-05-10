import os 
import time
import json
import requests
from dotenv import load_dotenv
from diskcache import Cache

cache = Cache("api_cache")
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

@cache.memoize(expire=86400) # Cache results for 1 day (86,400 seconds)
def fetch_from_api(endpoint_path):
    """Fetch data from the football-data.org API. Returns parsed JSON, or None on 404."""
    url = BASE_URL + "/" + endpoint_path
    headers = {"X-Auth-Token": API_KEY}
    response = _do_get(url, headers)
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        time.sleep(retry_after)
        response = _do_get(url, headers)
    if response.status_code == requests.codes.not_found:  # 404 means resource doesn't exist — caller decides UX, so return None
        return None
    response.raise_for_status()
    requests_available = int(response.headers.get("X-Requests-Available-Minute", 100000)) # missing header should not trigger sleep
    if requests_available <= 2: # Proactive throttle
        seconds_until_reset = int(response.headers.get("X-RequestCounter-Reset", 60))
        time.sleep(seconds_until_reset)
    return response.json()

def get_with_cache(cache_key, ttl_seconds, endpoint_path):
    """Get data from cache if available and not expired, otherwise fetch from API and cache it."""
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    data = fetch_from_api(endpoint_path)
    cache.set(cache_key, data, expire=ttl_seconds)
    return data

def get_competition():
    """Get the World Cup competition data"""
    return get_with_cache(cache_key="competition_wc", ttl_seconds=86400, endpoint_path="competitions/WC")

def get_matches():
    """Get the matches for the World Cup"""
    return get_with_cache(cache_key="matches_wc", ttl_seconds=900, endpoint_path="competitions/WC/matches")

def get_standings():
    """Get the standings for the World Cup"""
    return get_with_cache(cache_key="standings_wc", ttl_seconds=900, endpoint_path="competitions/WC/standings")

if __name__ == "__main__":
    # Test 1: happy path
    print("Test 1 - happy path:")
    data = fetch_from_api("competitions/WC")
    print(f"  {data['name']}")
    # Test 3: 404 path
    print("Test 3 - 404 returns None:")
    result = fetch_from_api("competitions/WC/matches/99999999")
    print(f"  {result}")

    # Test 2 LAST because it raises and stops execution
    print("Test 2 - 400 raises:")
    fetch_from_api("competitions/NOT_REAL")