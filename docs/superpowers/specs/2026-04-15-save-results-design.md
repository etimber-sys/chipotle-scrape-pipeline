# Design: Save Firecrawl Results as Markdown Files

**Date:** 2026-04-15
**Status:** Approved

## Goal

Extend `scrape_pipeline.py` to persist each Firecrawl search result as a markdown file in `knowledge/raw/`.

## Approach

Add a single function `save_results(results, run_date)` to `scrape_pipeline.py`, called after the API response is parsed. No new files or modules are introduced.

## Filename Format

```
knowledge/raw/YYYY-MM-DD_<slugified-url>.md
```

Slug rules: lowercase the URL, strip `https://`, replace non-alphanumeric characters with `-`, collapse consecutive dashes.

Example:
```
knowledge/raw/2026-04-15_ir-chipotle-com-news-releases.md
```

## File Content

Each file contains YAML frontmatter followed by the scraped markdown body:

```markdown
---
url: https://ir.chipotle.com/news-releases
title: News Releases - Chipotle Mexican Grill
description: These are news releases related to our Investor efforts.
date_scraped: 2026-04-15
---

# News Releases
...
```

## Directory Creation

`knowledge/raw/` is created via `Path.mkdir(parents=True, exist_ok=True)` at the start of `save_results()`. No manual setup required.

## Error Handling

If a result has no `markdown` field (e.g. results blocked by cookie consent walls), the file is still written with an empty body so the frontmatter metadata is preserved.

## What Does Not Change

- The Firecrawl API call and payload are unchanged.
- `print(response)` and `print(response.text)` debug lines remain unless separately removed.
- No new dependencies are introduced (`pathlib` and `datetime` are stdlib).
