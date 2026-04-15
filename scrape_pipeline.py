import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import requests


def slugify_url(url: str) -> str:
    slug = re.sub(r"https?://", "", url)
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower())
    return slug.strip("-")


load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

# --- Step 01: Search + scrape with Firecrawl ---

api_url = "https://api.firecrawl.dev/v2/search"

headers = {
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "query": "Chipotle investor relations press releases",
    "limit": 5,
    "scrapeOptions": {"formats": ["markdown"]}
}

response = requests.post(api_url, headers=headers, json=payload)

print(response)
print(response.text)