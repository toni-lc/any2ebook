from pathlib import Path

from any2ebook import clippings_ingest, clippings_to_epub
from any2ebook.any2ebook import main

DEMO_URLS = [
    "https://gutenberg.org/cache/epub/7256/pg7256-images.html",
    "https://www.gutenberg.org/cache/epub/1064/pg1064-images.html",
]


def write_demo_links_file(path: Path) -> None:
    path.write_text("\n".join(DEMO_URLS) + "\n", encoding="utf8")


def reset_demo_database(db_path: Path) -> None:
    for path in db_path.parent.glob(db_path.name + "*"):
        if path.is_file():
            path.unlink()


def main_demo() -> None:
    scripts_dir = Path(__file__).resolve().parent
    links_file = scripts_dir / "demo-links.txt"
    output_path = scripts_dir / "example.epub"
    db_path = scripts_dir / "any2ebook.db"
    reset_demo_database(db_path)
    clippings_ingest.ensure_db_path = lambda: db_path
    clippings_to_epub.ensure_db_path = lambda: db_path
    write_demo_links_file(links_file)
    main(["--file", str(links_file), "--output", str(output_path)])


if __name__ == "__main__":
    main_demo()
