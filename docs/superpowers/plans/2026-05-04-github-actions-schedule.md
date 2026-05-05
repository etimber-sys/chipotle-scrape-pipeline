# GitHub Actions Scheduled Scrape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a GitHub Actions workflow that runs the Chipotle scrape pipeline daily at 11:00 UTC, commits fresh `knowledge/raw/` markdown files back to the repo, and surfaces failures visibly in the Actions tab.

**Architecture:** A single workflow file (`.github/workflows/daily-scrape.yml`) defines one job with sequential steps: checkout → install deps → run tests → run scraper → conditional git commit. The built-in `GITHUB_TOKEN` handles the push; `FIRECRAWL_API_KEY` is stored as a repository secret.

**Tech Stack:** GitHub Actions, `actions/checkout@v4`, `actions/setup-python@v5`, Python 3.12, pytest, git CLI

---

### Task 1: Create the workflow directory and file

**Files:**
- Create: `.github/workflows/daily-scrape.yml`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create `.github/workflows/daily-scrape.yml`** with the following exact content:

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

- [ ] **Step 3: Validate the YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/daily-scrape.yml'))"`

Expected: No output (no error means valid YAML).

If Python's `pyyaml` is not installed: `pip install pyyaml` then re-run.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/daily-scrape.yml
git commit -m "feat: add daily GitHub Actions scrape workflow"
```

---

### Task 2: Add the repository secret on GitHub

This is a manual step in the GitHub web UI — it cannot be automated.

- [ ] **Step 1: Navigate to the secret settings**

Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

- [ ] **Step 2: Add the secret**

- **Name:** `FIRECRAWL_API_KEY`
- **Value:** your Firecrawl API key (the value from your local `.env` file — starts with `fc-`)

Click **Add secret**.

- [ ] **Step 3: Verify the secret appears in the list**

You should see `FIRECRAWL_API_KEY` listed under **Repository secrets**. The value will be masked — that's expected.

---

### Task 3: Push and verify with a manual trigger

- [ ] **Step 1: Push the branch to GitHub**

```bash
git push
```

- [ ] **Step 2: Trigger the workflow manually**

Go to your repo on GitHub → **Actions** → **Daily Chipotle Scrape** → **Run workflow** → **Run workflow** (default branch, no inputs needed).

- [ ] **Step 3: Watch the run**

Click into the running job. Verify each step turns green in order:
1. Set up job
2. actions/checkout@v4
3. actions/setup-python@v5
4. Install dependencies
5. Run tests
6. Run scraper
7. Commit scraped files

- [ ] **Step 4: Confirm the commit landed**

After the run completes, go to the repo's **Code** tab. You should see a new commit authored by `github-actions[bot]` with message `chore: daily scrape YYYY-MM-DD [skip ci]` and updated files under `knowledge/raw/`.

If the scraper finds no new content (all URLs were already scraped today), the "Commit scraped files" step will succeed silently with no new commit — that is correct behavior.

---

## Troubleshooting Reference

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Run tests` step fails | `slugify_url` or `save_results` not importable | Check that `scrape_pipeline.py` guards module-level API calls with `if __name__ == "__main__":` |
| `Run scraper` exits with 401 | Secret not set or misspelled | Re-check secret name is exactly `FIRECRAWL_API_KEY` |
| `git push` fails with 403 | `contents: write` permission missing | Confirm the `permissions` block is under `jobs.scrape`, not at workflow level |
| Workflow never appears in Actions tab | YAML syntax error | Re-run the `python -c "import yaml..."` validation from Task 1 Step 3 |
