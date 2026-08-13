from pathlib import Path

import pytest

from any2ebook import any2ebook


def test_main_builds_config_from_file_and_output_args(monkeypatch, tmp_path: Path):
    links_file = tmp_path / "blablabla.links"
    links_file.write_text("https://example.com\n", encoding="utf8")
    output_path = tmp_path / "book.epub"

    called = {}

    def fake_run(cfg):
        called["config"] = cfg
        return True

    monkeypatch.setattr("any2ebook.any2ebook.run", fake_run)

    any2ebook.main(["--file", str(links_file), "--output", str(output_path)])

    assert called["config"].input_path == links_file
    assert called["config"].clippings_path is None
    assert called["config"].output_path == output_path
    assert called["config"].config_path is None


def test_main_builds_config_from_obsidian_and_output_args(monkeypatch, tmp_path: Path):
    obsidian_path = tmp_path / "vault"
    obsidian_path.mkdir()
    output_path = tmp_path / "book.epub"

    called = {}

    def fake_run(cfg):
        called["config"] = cfg
        return True

    monkeypatch.setattr("any2ebook.any2ebook.run", fake_run)

    any2ebook.main(["--obsidian", str(obsidian_path), "--output", str(output_path)])

    assert called["config"].clippings_path == obsidian_path
    assert called["config"].input_path is None
    assert called["config"].output_path == output_path


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--output", "book.epub"],
        ["--file", "links.txt"],
        ["--obsidian", "vault"],
        ["--file", "links.txt", "--obsidian", "vault", "--output", "book.epub"],
    ],
)
def test_main_rejects_invalid_argument_combinations(args: list[str], tmp_path: Path):
    with pytest.raises(SystemExit):
        any2ebook.main(args)


def test_main_rejects_missing_input_paths(tmp_path: Path):
    with pytest.raises(SystemExit):
        any2ebook.main(
            ["--file", str(tmp_path / "missing.txt"), "--output", str(tmp_path / "book.epub")]
        )

    with pytest.raises(SystemExit):
        any2ebook.main(
            ["--obsidian", str(tmp_path / "missing"), "--output", str(tmp_path / "book.epub")]
        )


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


def test_run_test_mode_is_non_interactive_and_uses_links_file(monkeypatch, tmp_path: Path):
    called = {}

    def fake_ingest_run(cfg, dry_run=False, links_file=None):
        called["config"] = cfg
        called["dry_run"] = dry_run
        called["links_file"] = links_file
        return {"ready_items": 1, "warnings": 0}

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
    assert called["config"].input_path == called["links_file"]
    assert called["config"].output_path is not None
