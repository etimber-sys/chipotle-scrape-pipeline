# Save Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `save_results()` function to `scrape_pipeline.py` that writes each Firecrawl search result as a YAML-frontmatter markdown file under `knowledge/raw/`.

**Architecture:** A `slugify_url()` helper converts a URL to a safe filename component. `save_results()` creates the output directory, iterates over results, builds filenames from the run date and slug, and writes frontmatter + markdown body. Both functions live in `scrape_pipeline.py`; no new files are added.

**Tech Stack:** Python stdlib only (`pathlib`, `datetime`, `re`) — no new dependencies.

---

### Task 1: Add `slugify_url()` and test it

**Files:**
- Modify: `scrape_pipeline.py`
- Create: `tests/test_scrape_pipeline.py`

- [ ] **Step 1: Create the tests directory and write the failing test**

Create `tests/__init__.py` (empty) and `tests/test_scrape_pipeline.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrape_pipeline import slugify_url


def test_slugify_url_basic():
    assert slugify_url("https://ir.chipotle.com/news-releases") == "ir-chipotle-com-news-releases"


def test_slugify_url_strips_trailing_slash():
    assert slugify_url("https://ir.chipotle.com/") == "ir-chipotle-com"


def test_slugify_url_collapses_dashes():
    assert slugify_url("https://ir.chipotle.com/Financial-Releases") == "ir-chipotle-com-financial-releases"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
venv/Scripts/python -m pytest tests/test_scrape_pipeline.py -v
```

Expected: `ImportError: cannot import name 'slugify_url'`

- [ ] **Step 3: Add `slugify_url()` to `scrape_pipeline.py`**

Add after the existing imports (after `import requests`), before `load_dotenv()`:

```python
def slugify_url(url: str) -> str:
    slug = re.sub(r"https?://", "", url)
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower())
    return slug.strip("-")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
venv/Scripts/python -m pytest tests/test_scrape_pipeline.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/
git commit -m "feat: add slugify_url helper with tests"
```

---

### Task 2: Add `save_results()` and test it

**Files:**
- Modify: `scrape_pipeline.py`
- Modify: `tests/test_scrape_pipeline.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_scrape_pipeline.py`:

```python
import tempfile
from datetime import date
from scrape_pipeline import save_results


def test_save_results_creates_files():
    results = [
        {
            "url": "https://ir.chipotle.com/news-releases",
            "title": "News Releases",
            "description": "Investor news.",
            "markdown": "# News Releases\n\nSome content.",
        }
    ]
    run_date = date(2026, 4, 15)

    with tempfile.TemporaryDirectory() as tmpdir:
        save_results(results, run_date, output_dir=Path(tmpdir))
        files = list(Path(tmpdir).iterdir())
        assert len(files) == 1
        assert files[0].name == "2026-04-15_ir-chipotle-com-news-releases.md"


def test_save_results_file_content():
    results = [
        {
            "url": "https://ir.chipotle.com/news-releases",
            "title": "News Releases",
            "description": "Investor news.",
            "markdown": "# News Releases\n\nSome content.",
        }
    ]
    run_date = date(2026, 4, 15)

    with tempfile.TemporaryDirectory() as tmpdir:
        save_results(results, run_date, output_dir=Path(tmpdir))
        content = (Path(tmpdir) / "2026-04-15_ir-chipotle-com-news-releases.md").read_text()

    assert "url: https://ir.chipotle.com/news-releases" in content
    assert "title: News Releases" in content
    assert "description: Investor news." in content
    assert "date_scraped: 2026-04-15" in content
    assert "# News Releases" in content


def test_save_results_missing_markdown():
    """Results with no markdown field still write a file with frontmatter."""
    results = [
        {
            "url": "https://example.com/page",
            "title": "Example",
            "description": "Cookie wall.",
        }
    ]
    run_date = date(2026, 4, 15)

    with tempfile.TemporaryDirectory() as tmpdir:
        save_results(results, run_date, output_dir=Path(tmpdir))
        content = (Path(tmpdir) / "2026-04-15_example-com-page.md").read_text()

    assert "url: https://example.com/page" in content
    assert content.endswith("---\n\n")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
venv/Scripts/python -m pytest tests/test_scrape_pipeline.py -v
```

Expected: `ImportError: cannot import name 'save_results'`

- [ ] **Step 3: Add `save_results()` to `scrape_pipeline.py`**

Add `from datetime import date` to the top imports. Then add this function directly below `slugify_url()`:

```python
def save_results(results: list, run_date: date, output_dir: Path = Path("knowledge/raw")) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = run_date.isoformat()
    for result in results:
        slug = slugify_url(result["url"])
        filename = f"{date_str}_{slug}.md"
        frontmatter = (
            f"---\n"
            f"url: {result['url']}\n"
            f"title: {result['title']}\n"
            f"description: {result.get('description', '')}\n"
            f"date_scraped: {date_str}\n"
            f"---\n\n"
        )
        body = result.get("markdown", "")
        (output_dir / filename).write_text(frontmatter + body, encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
venv/Scripts/python -m pytest tests/test_scrape_pipeline.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/test_scrape_pipeline.py
git commit -m "feat: add save_results function with tests"
```

---

### Task 3: Wire `save_results()` into the script's main flow

**Files:**
- Modify: `scrape_pipeline.py`

- [ ] **Step 1: Add the call to `save_results()` after the API response**

Replace the bottom of `scrape_pipeline.py` (the two `print` lines) with:

```python
response = requests.post(api_url, headers=headers, json=payload)

print(response)
print(response.text)

data = response.json()
results = data["data"]["web"]
save_results(results, date.today())
print(f"Saved {len(results)} results to knowledge/raw/")
```

- [ ] **Step 2: Run the script end-to-end**

```bash
venv/Scripts/python scrape_pipeline.py
```

Expected output ends with: `Saved 5 results to knowledge/raw/`

- [ ] **Step 3: Verify files were created**

```bash
ls knowledge/raw/
```

Expected: 5 `.md` files named `2026-04-15_<slug>.md`

- [ ] **Step 4: Spot-check one file**

```bash
head -8 "knowledge/raw/2026-04-15_ir-chipotle-com-news-releases.md"
```

Expected:
```
---
url: https://ir.chipotle.com/news-releases
title: News Releases - Chipotle Mexican Grill
description: These are news releases...
date_scraped: 2026-04-15
---
```

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py knowledge/raw/
git commit -m "feat: wire save_results into pipeline, persist scraped markdown"
```
