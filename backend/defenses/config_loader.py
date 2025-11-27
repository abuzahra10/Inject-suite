from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

CONFIG_DIR = Path(__file__).resolve().parent / "config"


@lru_cache(maxsize=None)
def load_config(name: str) -> Dict[str, Any]:
    path = CONFIG_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Defense config '{name}' not found at {path}.")
    return json.loads(path.read_text(encoding="utf-8"))
