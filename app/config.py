import json
import os
import sys
from pathlib import Path

APP_NAME = "PhotoCompressorService"
VERSION = "1.0.1"
GITHUB_URL = "https://github.com/Pro100NeFarT/PhotoCompressorService"

DEFAULT_CONFIG = {
    "host": "127.0.0.1",
    "port": 8788,
    "max_upload_mb": 25,
    "log_level": "INFO",
    "compression": {
        "max_width": 1920,
        "max_height": 1920,
        "max_size_kb": 300,
        "quality_start": 90,
        "quality_min": 40,
        "quality_step": 5,
    },
    "update": {
        "enabled": True,
        "github_repo": "Pro100NeFarT/PhotoCompressorService",
        "check_interval_hours": 24,
    },
}


def _program_data_dir() -> Path:
    base = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    return Path(base) / APP_NAME


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def config_dir() -> Path:
    if _is_frozen():
        return _program_data_dir()
    return Path(__file__).resolve().parent.parent


def config_path() -> Path:
    return config_dir() / "config.json"


def log_dir() -> Path:
    if _is_frozen():
        d = _program_data_dir() / "logs"
    else:
        d = Path(__file__).resolve().parent.parent / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> dict:
    path = config_path()
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            cfg = _merge(cfg, user_cfg)
        except Exception as exc:
            print(f"Попередження: не вдалося прочитати {path}: {exc}. Використано дефолти.")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    return cfg
