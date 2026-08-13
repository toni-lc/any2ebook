import datetime
import runpy
import shutil
from pathlib import Path

from ebooklib import epub

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
OUTPUT_PATH = SCRIPTS_DIR / "example.epub"
DB_PATH = SCRIPTS_DIR / "any2ebook.db"
DEMO_LINKS_PATH = SCRIPTS_DIR / "demo-links.txt"
DEMO_OBSIDIAN_PATH = SCRIPTS_DIR / "demo-obsidian-vault"
DEMO_STAGING_PATH = SCRIPTS_DIR / "staging"


def _cleanup_demo_artifacts() -> None:
    for path in DB_PATH.parent.glob(DB_PATH.name + "*"):
        if path.is_file():
            path.unlink()
    if OUTPUT_PATH.exists():
        OUTPUT_PATH.unlink()
    if DEMO_LINKS_PATH.exists():
        DEMO_LINKS_PATH.unlink()
    if DEMO_OBSIDIAN_PATH.exists():
        shutil.rmtree(DEMO_OBSIDIAN_PATH)
    if DEMO_STAGING_PATH.exists():
        shutil.rmtree(DEMO_STAGING_PATH)


def _fake_content(url: str) -> dict[str, str]:
    title_by_url = {
        "https://gutenberg.org/cache/epub/7256/pg7256-images.html": "The Gift of the Magi",
        "https://www.gutenberg.org/cache/epub/1064/pg1064-images.html": (
            "The Masque of the Red Death"
        ),
    }
    title = title_by_url[url]
    return {"title": title, "content": f"<h1>{title}</h1><p>Demo content.</p>"}


def _assert_demo_epub_metadata() -> None:
    book = epub.read_epub(str(OUTPUT_PATH))
    title = book.get_metadata("DC", "title")[0][0]
    creator = book.get_metadata("DC", "creator")[0][0]

    assert title == f"Collected Articles -{datetime.datetime.now().strftime('%Y-%m-%d')}"
    assert creator == "Unknown"


def test_demo_obsidian_creates_epub_with_expected_metadata(monkeypatch):
    """Run the Obsidian demo and verify its EPUB metadata."""
    _cleanup_demo_artifacts()
    monkeypatch.setattr("any2ebook.html2ebook.extract_website_content", _fake_content)

    try:
        runpy.run_path(str(SCRIPTS_DIR / "demo-obsidian.py"), run_name="__main__")

        assert DB_PATH.exists()
        assert OUTPUT_PATH.exists()
        _assert_demo_epub_metadata()
    finally:
        _cleanup_demo_artifacts()


def test_demo_txt_creates_epub_with_expected_metadata(monkeypatch):
    """Run the text-file demo and verify its EPUB metadata."""
    _cleanup_demo_artifacts()
    monkeypatch.setattr("any2ebook.html2ebook.extract_website_content", _fake_content)

    try:
        runpy.run_path(str(SCRIPTS_DIR / "demo-txt.py"), run_name="__main__")

        assert DB_PATH.exists()
        assert OUTPUT_PATH.exists()
        _assert_demo_epub_metadata()
    finally:
        _cleanup_demo_artifacts()
