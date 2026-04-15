import os
import re
import time
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import requests


def slugify_url(url: str) -> str:
    slug = re.sub(r"https?://", "", url)
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower())
    return slug.strip("-")


def _yaml_scalar(value: str) -> str:
    value = value.replace('\r', '').replace('\n', ' ')
    if ': ' in value or value.startswith(('{', '[', '|', '>', '-', '?', '!')):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def save_results(results: list, run_date: date, output_dir: Path = Path("knowledge/raw")) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = run_date.isoformat()
    for result in results:
        slug = slugify_url(result["url"])
        filename = f"{date_str}_{slug}.md"
        frontmatter = (
            f"---\n"
            f"url: {result['url']}\n"
            f"title: {_yaml_scalar(result['title'])}\n"
            f"description: {_yaml_scalar(result.get('description', ''))}\n"
            f"date_scraped: {date_str}\n"
            f"---\n\n"
        )
        body = result.get("markdown", "")
        (output_dir / filename).write_text(frontmatter + body, encoding="utf-8")


if __name__ == "__main__":
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
