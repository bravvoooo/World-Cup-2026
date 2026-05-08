import os 
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

def fetch_from_api(endpoint_path):
    url = BASE_URL + "/" + endpoint_path
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

data = fetch_from_api("competitions/WC")
print(data["name"])
