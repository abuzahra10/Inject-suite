"""Heuristic injector detection."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List


SUSPICIOUS_TOKENS = {
    "ignore previous",
    "override",
    "rot13",
    "base64",
    "extract secret",
    "exfiltrate",
    "system prompt",
}


@dataclass
class DetectionResult:
    score: float
    triggers: List[str]

    def as_dict(self) -> Dict[str, object]:
        return {"score": self.score, "triggers": self.triggers}


def detect(prompt: str, threshold: float = 0.3) -> DetectionResult:
    """Return a suspicion score based on keyword and formatting analysis."""

    lowered = prompt.lower()
    triggers = [token for token in SUSPICIOUS_TOKENS if token in lowered]

    keyword_score = len(triggers) / len(SUSPICIOUS_TOKENS)

    # uppercase ratio heuristic
    uppercase_chars = sum(1 for c in prompt if c.isupper())
    total_letters = sum(1 for c in prompt if c.isalpha()) or 1
    casing_score = uppercase_chars / total_letters

    score = max(keyword_score, casing_score)
    score = min(1.0, round(score, 3))

    if score >= threshold and "alert" not in triggers:
        triggers.append("threshold")

    return DetectionResult(score=score, triggers=triggers)
