from pathlib import Path

from any2ebook import clippings_ingest, clippings_to_epub
from any2ebook.any2ebook import main

DEMO_URLS = [
    "https://gutenberg.org/cache/epub/7256/pg7256-images.html",
    "https://www.gutenberg.org/cache/epub/1064/pg1064-images.html",
]


def write_demo_obsidian_files(vault_dir: Path) -> None:
    clippings_dir = vault_dir / "Clippings"
    clippings_dir.mkdir(parents=True, exist_ok=True)
    for idx, url in enumerate(DEMO_URLS, start=1):
        (clippings_dir / f"demo-{idx}.md").write_text(
            "\n".join(
                [
                    "---",
                    f'source: "{url}"',
                    "---",
                    f"# Demo link {idx}",
                    "",
                ]
            ),
            encoding="utf8",
        )


def reset_demo_database(db_path: Path) -> None:
    for path in db_path.parent.glob(db_path.name + "*"):
        if path.is_file():
            path.unlink()


def main_demo() -> None:
    scripts_dir = Path(__file__).resolve().parent
    vault_dir = scripts_dir / "demo-obsidian-vault"
    output_path = scripts_dir / "example.epub"
    db_path = scripts_dir / "any2ebook.db"
    reset_demo_database(db_path)
    clippings_ingest.ensure_db_path = lambda: db_path
    clippings_to_epub.ensure_db_path = lambda: db_path
    write_demo_obsidian_files(vault_dir)
    main(["--obsidian", str(vault_dir), "--output", str(output_path)])


if __name__ == "__main__":
    main_demo()
