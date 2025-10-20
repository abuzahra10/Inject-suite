"""Prompt sanitization utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


REMOVAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"ignore prior instructions",
        r"system override",
        r"rot13",
        r"base64",
        r"exfiltrate",
    ]
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
