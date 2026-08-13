from pathlib import Path

import pytest

from any2ebook import any2ebook


def test_main_builds_config_from_file_and_output_args(monkeypatch, tmp_path: Path):
    links_file = tmp_path / "links.txt"
    links_file.write_text("https://example.com\n", encoding="utf8")
    output_path = tmp_path / "book.epub"

    called = {}

    def fake_run(cfg, links_file=None, input_dir=None, dry_run=False):
        called["config"] = cfg
        called["links_file"] = links_file
        called["input_dir"] = input_dir
        called["dry_run"] = dry_run
        return True

    monkeypatch.setattr("any2ebook.any2ebook.run", fake_run)

    with pytest.raises(SystemExit) as exc:
        any2ebook.main(["--file", str(links_file), "--output", str(output_path)])

    assert exc.value.code == 0
    assert called["config"].input_path == links_file
    assert called["config"].clippings_path is None
    assert called["config"].output_path == output_path
    assert called["config"].config_path is None
    assert called["input_dir"] is None
    assert called["dry_run"] is False


def test_main_builds_config_from_obsidian_and_output_args(monkeypatch, tmp_path: Path):
    obsidian_path = tmp_path / "vault"
    obsidian_path.mkdir()
    output_path = tmp_path / "book.epub"

    called = {}

    def fake_run(cfg, links_file=None, input_dir=None, dry_run=False):
        called["config"] = cfg
        called["links_file"] = links_file
        called["input_dir"] = input_dir
        called["dry_run"] = dry_run
        return True

    monkeypatch.setattr("any2ebook.any2ebook.run", fake_run)

    with pytest.raises(SystemExit) as exc:
        any2ebook.main(["--obsidian", str(obsidian_path), "--output", str(output_path)])

    assert exc.value.code == 0
    assert called["config"].clippings_path == obsidian_path
    assert called["config"].input_path is None
    assert called["config"].output_path == output_path
    assert called["input_dir"] is None
    assert called["dry_run"] is False


def test_main_passes_input_dir_to_run(monkeypatch, tmp_path: Path):
    input_dir = tmp_path / "inbox"
    input_dir.mkdir()
    output_path = tmp_path / "book.epub"

    called = {}

    def fake_run(cfg, links_file=None, input_dir=None, dry_run=False):
        called["config"] = cfg
        called["links_file"] = links_file
        called["input_dir"] = input_dir
        called["dry_run"] = dry_run
        return True

    monkeypatch.setattr("any2ebook.any2ebook.run", fake_run)

    with pytest.raises(SystemExit) as exc:
        any2ebook.main(["--input-dir", str(input_dir), "--output", str(output_path)])

    assert exc.value.code == 0
    assert called["config"].input_path is None
    assert called["config"].clippings_path is None
    assert called["config"].output_path == output_path
    assert called["links_file"] is None
    assert called["input_dir"] == input_dir
    assert called["dry_run"] is False


def test_main_passes_dry_run_flag_to_run(monkeypatch, tmp_path: Path):
    links_file = tmp_path / "links.txt"
    links_file.write_text("https://example.com\n", encoding="utf8")
    output_path = tmp_path / "book.epub"

    called = {}

    def fake_run(cfg, links_file=None, input_dir=None, dry_run=False):
        called["config"] = cfg
        called["links_file"] = links_file
        called["input_dir"] = input_dir
        called["dry_run"] = dry_run
        return True

    monkeypatch.setattr("any2ebook.any2ebook.run", fake_run)

    with pytest.raises(SystemExit) as exc:
        any2ebook.main(["--dry-run", "--file", str(links_file), "--output", str(output_path)])

    assert exc.value.code == 0
    assert called["config"].input_path == links_file
    assert called["input_dir"] is None
    assert called["dry_run"] is True


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--output", "book.epub"],
        ["--file", "links.txt"],
        ["--obsidian", "vault"],
        ["--input-dir", "inbox"],
        ["--file", "links.txt", "--obsidian", "vault", "--output", "book.epub"],
        ["--file", "links.txt", "--input-dir", "inbox", "--output", "book.epub"],
    ],
)
def test_main_rejects_invalid_argument_combinations(args: list[str]):
    with pytest.raises(SystemExit):
        any2ebook.main(args)


def test_main_rejects_missing_input_paths(tmp_path: Path):
    output_path = tmp_path / "book.epub"

    with pytest.raises(SystemExit):
        any2ebook.main(["--file", str(tmp_path / "missing.txt"), "--output", str(output_path)])
    with pytest.raises(SystemExit):
        any2ebook.main(["--obsidian", str(tmp_path / "missing"), "--output", str(output_path)])
    with pytest.raises(SystemExit):
        any2ebook.main(["--input-dir", str(tmp_path / "missing"), "--output", str(output_path)])


def test_main_rejects_missing_output_parent(tmp_path: Path):
    links_file = tmp_path / "links.txt"
    links_file.write_text("https://example.com\n", encoding="utf8")

    with pytest.raises(SystemExit):
        any2ebook.main(
            [
                "--file",
                str(links_file),
                "--output",
                str(tmp_path / "missing" / "book.epub"),
            ]
        )


def test_main_info_prints_database_path_without_input_args(monkeypatch, capsys, tmp_path: Path):
    db_path = tmp_path / "any2ebook.db"
    monkeypatch.setattr("any2ebook.any2ebook.ensure_db_path", lambda: db_path)

    any2ebook.main(["info"])

    assert capsys.readouterr().out == f"{db_path}\n"


def test_run_test_mode_is_non_interactive_and_uses_links_file(monkeypatch):
    called = {}

    def fake_ingest_run(cfg, dry_run=False, links_file=None, input_dir=None):
        called["config"] = cfg
        called["dry_run"] = dry_run
        called["links_file"] = links_file
        called["input_dir"] = input_dir
        return {
            "ready_items": 1,
            "warnings": 0,
            "files_seen": 1,
            "files_processed": 1,
            "files_skipped_unchanged": 0,
        }

    monkeypatch.setattr("any2ebook.any2ebook.clippings_ingest.run", fake_ingest_run)
    monkeypatch.setattr(
        "builtins.input",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("input() should not be called")
        ),
    )

    ok = any2ebook.run_test_mode()

    assert ok is True
    assert called["dry_run"] is True
    assert called["links_file"] is not None
    assert called["links_file"].suffix == ".txt"
    assert called["input_dir"] is None
    assert called["config"].input_path == called["links_file"]
    assert called["config"].output_path is not None
