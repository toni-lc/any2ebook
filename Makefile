install:
	uv tool install git+https://github.com/tonilatorrec/any2ebook.git

.PHONY: update-deps
update-deps:
	uv sync --frozen

.PHONY: test
test:
	uv run python -m pytest

.PHONY: lint
lint: 
	uv run ruff check ./src ./tests --fix

.PHONY: format
format:
	uv run ruff format ./src ./tests

.PHONY: upgrade
upgrade:
	uv tool upgrade any2ebook

.PHONY: demo-obsidian
demo-obsidian:
	uv run python scripts/demo-obsidian.py

.PHONY: demo-txt
demo-txt:
	uv run python scripts/demo-txt.py
