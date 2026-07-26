"""Loads config.yaml into a simple object with sane defaults."""

from pathlib import Path
from types import SimpleNamespace
import yaml


DEFAULTS = {
    "input": {
        "directory": "./images/input",
        "extensions": [".png", ".jpg", ".jpeg", ".tiff"],
    },
    "output": {
        "directory": "./images/output",
        "suffix": "_denoised",
    },
    "method": "non_local_means",  # or "bilateral"
    "bilateral": {
        "diameter": 9,
        "sigma_color": 75,
        "sigma_space": 75,
    },
    "non_local_means": {
        "h": 10,
        "template_window_size": 7,
        "search_window_size": 21,
    },
    "dark_frame": {
        "enabled": False,
        "path": "./dark_frame.png",
    },
}


def _merge(defaults: dict, overrides: dict) -> dict:
    """Shallow-merge overrides into defaults, one level deep (good enough here)."""
    result = dict(defaults)
    for key, value in (overrides or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = {**result[key], **value}
        else:
            result[key] = value
    return result


def _to_namespace(d: dict) -> SimpleNamespace:
    return SimpleNamespace(**{
        k: _to_namespace(v) if isinstance(v, dict) else v
        for k, v in d.items()
    })


def load_config(path: str = "config.yaml") -> SimpleNamespace:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: '{path}'")

    with config_path.open("r") as f:
        raw = yaml.safe_load(f) or {}

    merged = _merge(DEFAULTS, raw)

    # Basic sanity checks -- fail fast with a clear message rather than
    # letting OpenCV throw a cryptic error mid-batch.
    method = merged["method"]
    if method not in ("bilateral", "non_local_means"):
        raise ValueError(f"method must be 'bilateral' or 'non_local_means', got '{method}'")

    nlm = merged["non_local_means"]
    if nlm["template_window_size"] % 2 == 0:
        raise ValueError(f"non_local_means.template_window_size must be odd, got {nlm['template_window_size']}")
    if nlm["search_window_size"] % 2 == 0:
        raise ValueError(f"non_local_means.search_window_size must be odd, got {nlm['search_window_size']}")
    if nlm["search_window_size"] < nlm["template_window_size"]:
        raise ValueError("non_local_means.search_window_size must be >= template_window_size")

    input_dir_raw = merged["input"]["directory"]
    input_dir = Path(input_dir_raw)
    if not input_dir.is_absolute():
        input_dir = config_path.resolve().parent / input_dir
    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: '{input_dir}'")

    dark_frame = merged["dark_frame"]
    if dark_frame["enabled"]:
        dark_path = Path(dark_frame["path"])
        if not dark_path.is_absolute():
            dark_path = config_path.resolve().parent / dark_path
        if not dark_path.exists():
            raise ValueError(f"dark_frame.enabled is true but file does not exist: '{dark_path}'")
        # Store the resolved absolute path so main.py doesn't need to
        # re-derive it relative to the config file location.
        dark_frame["path"] = str(dark_path)

    return _to_namespace(merged)


if __name__ == "__main__":
    import sys
    cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
    print(cfg)