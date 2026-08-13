import os
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml


class ConfigNotFoundError(FileNotFoundError):
    pass


@dataclass(slots=True)
class Config:
    # stable fields (known at dev time)
    config_path: Path | None = None
    clippings_path: Path | None = None
    input_path: Path | None = None
    output_path: Path | None = None

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> "Config":
        """Load config from disk."""
        config_path = Path(path)
        if not config_path.exists():
            raise ConfigNotFoundError(config_path)
        with open(config_path, "r") as f:
            raw = yaml.safe_load(f) or {}
            # TODO: avoid Path('.') when the raw is ''
            return cls(
                config_path=config_path,
                clippings_path=(
                    Path(raw["clippings_path"]) if raw.get("clippings_path") is not None else None
                ),
                input_path=Path(raw["input_path"]) if raw.get("input_path") is not None else None,
                output_path=Path(raw["output_path"])
                if raw.get("output_path") is not None
                else None,
            )

    def save(self, config_path: Path | None = None) -> None:
        """Save to disk."""
        target_path = config_path or self.config_path
        if target_path is None:
            raise ValueError("config_path is required to save a config file")
        raw = asdict(self)
        out = dict()
        # TODO: create constant for all keys to be saved in config file
        for k in ("clippings_path", "input_path", "output_path"):
            out[k] = str(raw[k]) if raw[k] is not None else None
        with open(target_path, "w") as f:
            yaml.dump(out, f)
        self.config_path = target_path

    def validate(self) -> None:
        # TODO: implement?
        pass
