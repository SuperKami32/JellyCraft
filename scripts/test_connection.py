import os
import requests
from dotenv import load_dotenv

load_dotenv()

JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")

if not JELLYFIN_URL or not JELLYFIN_API_KEY:
    raise ValueError("Missing JELLYFIN_URL or JELLYFIN_API_KEY in .env")

headers = {
    "X-Emby-Token": JELLYFIN_API_KEY
}

url = f"{JELLYFIN_URL.rstrip('/')}/System/Info"

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()

print("Connected successfully.")
print(response.json())
