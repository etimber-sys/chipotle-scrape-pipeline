import sys
import tempfile
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrape_pipeline import slugify_url, save_results


def test_slugify_url_basic():
    assert slugify_url("https://ir.chipotle.com/news-releases") == "ir-chipotle-com-news-releases"


def test_slugify_url_strips_trailing_slash():
    assert slugify_url("https://ir.chipotle.com/") == "ir-chipotle-com"


def test_slugify_url_collapses_dashes():
    assert slugify_url("https://ir.chipotle.com/Financial-Releases") == "ir-chipotle-com-financial-releases"


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
