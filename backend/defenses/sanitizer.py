"""Prompt sanitization utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from defenses.config_loader import load_config


_SANITIZER_CONFIG = load_config("sanitizer")
REMOVAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in _SANITIZER_CONFIG.get("removal_patterns", [])
]


@dataclass
class SanitizationResult:
    clean_prompt: str
    removed_phrases: List[str]


def sanitize(prompt: str) -> SanitizationResult:
    """Strip known attack phrases and return the cleaned prompt."""

    removed: List[str] = []
    sanitized = prompt
    for pattern in REMOVAL_PATTERNS:
        matches = pattern.findall(sanitized)
        if matches:
            removed.extend(matches)
            sanitized = pattern.sub("", sanitized)

    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized).strip()

    return SanitizationResult(clean_prompt=sanitized, removed_phrases=removed)
