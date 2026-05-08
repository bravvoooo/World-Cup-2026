import os 
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

def fetch_from_api(endpoint_path):
    """Fetch data from the football-data.org API. Returns parsed JSON, or None on 404."""
    url = BASE_URL + "/" + endpoint_path
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers) # The purpose is to make a HTTP request
    if response.status_code == requests.codes.not_found:  # 404 means resource doesn't exist — caller decides UX, so return None
        return None
    response.raise_for_status()
    return response.json()

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