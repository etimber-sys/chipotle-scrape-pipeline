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
