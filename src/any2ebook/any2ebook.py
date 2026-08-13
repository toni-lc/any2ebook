import argparse
import tempfile
from pathlib import Path

from . import clippings_ingest, clippings_to_epub
from .config import Config
from .db import ensure_db_path


def run(
    config: Config,
    links_file: Path | None = None,
    input_dir: Path | None = None,
    dry_run: bool = False,
) -> bool:
    try:
        report = clippings_ingest.run(
            config,
            dry_run=dry_run,
            links_file=links_file or config.input_path,
            input_dir=input_dir,
        )
        if dry_run:
            print(
                "Dry-run results:",
                f"ready_items={report['ready_items']}",
                f"warnings={report['warnings']}",
                f"files_seen={report['files_seen']}",
                f"files_processed={report['files_processed']}",
                f"files_skipped_unchanged={report['files_skipped_unchanged']}",
                sep=" ",
            )
            return True

        clippings_to_epub.run(config)
        return True
    except Exception as e:
        print("Error:", e)
        return False


def run_test_mode() -> bool:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=True, encoding="utf8") as f:
        f.write("https://example.com\n")
        f.flush()
        output_path = Path(tempfile.gettempdir()) / "any2ebook-test.epub"
        config = Config(input_path=Path(f.name), output_path=output_path)
        report = clippings_ingest.run(config, dry_run=True, links_file=Path(f.name))
    print(
        "Test mode results:",
        f"ready_items={report['ready_items']}",
        f"warnings={report['warnings']}",
        sep=" ",
    )
    return True


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="any2ebook")
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-f",
        "--file",
        dest="input_file",
        help="Path to a text or JSON file containing URLs.",
    )
    input_group.add_argument(
        "--obsidian",
        help="Path to an Obsidian folder containing clipped Markdown files.",
    )
    input_group.add_argument(
        "--input-dir",
        dest="input_dir",
        help="Path to a folder with mixed .md/.json files to ingest.",
    )
    parser.add_argument(
        "--output",
        help="Output EPUB file path.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a self-contained test workflow (alias for `any2ebook test`).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be ingested without writing to DB or converting.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("test", help="Run a self-contained test workflow.")
    subparsers.add_parser("info", help="Print the database path.")
    args = parser.parse_args(argv)

    if args.test or args.command == "test":
        ok = run_test_mode()
        raise SystemExit(0 if ok else 1)
    if args.command == "info":
        print(ensure_db_path())
        return

    has_input = any(
        path is not None for path in (args.input_file, args.obsidian, args.input_dir)
    )
    if not has_input:
        parser.error("one of --obsidian, --file, or --input-dir is required")
    if args.output is None:
        parser.error("--output is required")

    input_path: Path | None = None
    obsidian_path: Path | None = None
    input_dir: Path | None = None
    output_path = Path(args.output)

    if args.input_file is not None:
        input_path = Path(args.input_file)
        if not input_path.exists() or not input_path.is_file():
            parser.error(f"--file must be an existing file: {input_path}")
    if args.obsidian is not None:
        obsidian_path = Path(args.obsidian)
        if not obsidian_path.exists() or not obsidian_path.is_dir():
            parser.error(f"--obsidian must be an existing folder: {obsidian_path}")
    if args.input_dir is not None:
        input_dir = Path(args.input_dir)
        if not input_dir.exists() or not input_dir.is_dir():
            parser.error(f"--input-dir must be an existing folder: {input_dir}")
    if not output_path.parent.exists() or not output_path.parent.is_dir():
        parser.error(f"--output parent folder must exist: {output_path.parent}")

    config = Config(
        clippings_path=obsidian_path,
        input_path=input_path,
        output_path=output_path,
    )
    ok = run(config, input_dir=input_dir, dry_run=args.dry_run)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
