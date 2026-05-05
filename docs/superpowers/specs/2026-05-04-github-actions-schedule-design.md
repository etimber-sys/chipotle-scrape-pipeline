# Design: GitHub Actions Scheduled Scrape Pipeline

**Date:** 2026-05-04
**Status:** Approved

## Goal

Run the Firecrawl scrape pipeline automatically every day via GitHub Actions, commit the resulting `knowledge/raw/` markdown files back to the repo, and surface failures visibly in the Actions tab.

## Trigger

```yaml
on:
  schedule:
    - cron: "0 11 * * *"   # 06:00 ET / 11:00 UTC daily
  workflow_dispatch:         # manual trigger from Actions tab
```

Daily at 11:00 UTC (6 AM Eastern). `workflow_dispatch` allows on-demand runs without editing code.

## Workflow Structure

Single job (`scrape`) on `ubuntu-latest`. Steps run sequentially; any failure aborts the job.

| Step | Action |
|------|--------|
| Checkout | `actions/checkout@v4` |
| Setup Python | `actions/setup-python@v5`, Python 3.12 |
| Install deps | `pip install -r requirements.txt` |
| Run tests | `pytest tests/` — aborts on failure |
| Run scraper | `python scrape_pipeline.py` |
| Commit output | `git add knowledge/raw/` + conditional commit + push |

## Secrets & Permissions

**Secret:** `FIRECRAWL_API_KEY` stored in repo **Settings → Secrets and variables → Actions**. Exposed as an environment variable at the job level.

**Permissions:** `contents: write` on the job — minimum scope needed to push the commit. Uses the built-in `GITHUB_TOKEN`; no PAT required.

## Commit Convention

```
chore: daily scrape YYYY-MM-DD [skip ci]
```

`[skip ci]` prevents the bot commit from re-triggering workflows. The commit is skipped entirely if `git diff --cached --quiet` finds no changed files (idempotent on days with no new content).

## Failure Handling

Failures surface in the GitHub Actions tab. GitHub sends an email notification by default for failed scheduled workflows. No issue automation or additional alerting.

## File Location

```
.github/workflows/daily-scrape.yml
```

## Full Workflow YAML

```yaml
name: Daily Chipotle Scrape

on:
  schedule:
    - cron: "0 11 * * *"
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    env:
      FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/

      - name: Run scraper
        run: python scrape_pipeline.py

      - name: Commit scraped files
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add knowledge/raw/
          git diff --cached --quiet || git commit -m "chore: daily scrape $(date -u +%Y-%m-%d) [skip ci]"
          git push
```

## What This Does Not Cover

- Query parameterization via `workflow_dispatch` inputs (can be added later)
- Artifact upload (output lives in git history only)
- Downstream processing of scraped files (separate pipeline concern)
